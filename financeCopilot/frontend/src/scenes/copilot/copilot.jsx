import React, { useState, useRef, useEffect } from "react";
import {
  Box,
  Typography,
  TextField,
  Button,
  IconButton,
  Avatar,
  CircularProgress,
  Tooltip,
  useTheme,
  Dialog,
} from "@mui/material";

import {
  SmartToy,
  Person,
  Send,
  AttachFile,
  Close,
  HourglassEmpty,
} from "@mui/icons-material";

import { toast } from "react-toastify";

import {
  sendCopilotMessage,
  saveTransactions,
  saveUserStocks,
  resolveUrl,
} from "../../util/api";
import { tokens } from "../../theme";

const Copilot = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [showTrackDialog, setShowTrackDialog] = useState(false);
  const [suggestedStocks, setSuggestedStocks] = useState([]);
  const [sources, setSources] = useState(null);
  const [showSources, setShowSources] = useState(false);
  const [trackingStep, setTrackingStep] = useState(null);
  const [stepHistory, setStepHistory] = useState([]);
  const [displayedSteps, setDisplayedSteps] = useState([]);
  // Custom deduplicated steps state
  const [customStepHistory, setCustomStepHistory] = useState([]);
  const lastDisplayedIndexRef = useRef(0);
  const [trackingActive, setTrackingActive] = useState(false);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  // New state and ref for delayed message logic
  const [readyToShowFinalMessage, setReadyToShowFinalMessage] = useState(false);
  const delayedBotMsgRef = useRef("");

  const theme = useTheme();
  const colors = tokens(theme.palette.mode);

  useEffect(() => {
    setMessages([
      {
        sender: "ai",
        text: "Hello! I'm your Finance Copilot. How can I help you today?",
      },
    ]);
  }, []);

  // Polling static job status for tracking step
  useEffect(() => {
    if (!trackingActive) return;

    const interval = setInterval(async () => {
      try {
        const res = await fetch(
          "http://localhost:5001/job-status/static-track-id"
        );
        const data = await res.json();
        console.log("Polling data:", data); // Debug log
        if (data?.success) {
          if (data.status?.step) {
            setTrackingStep(data.status.step);
          }
          if (Array.isArray(data.status?.steps)) {
            // Use deduplicated step history
            setCustomStepHistory((prev) => {
              const newSteps = data.status.steps.filter(
                (step) => !prev.includes(step)
              );
              return newSteps.length > 0 ? [...prev, ...newSteps] : prev;
            });
          }
        }

        if (
          data?.status?.status === "done" ||
          data?.status?.status === "failed"
        ) {
          clearInterval(interval);
          setTrackingStep(null);
          setTrackingActive(false);
        }
      } catch (err) {
        console.error("Polling error:", err);
      }
    }, 750);

    return () => clearInterval(interval);
  }, [trackingActive]);

  // Animate step display when customStepHistory updates (only show new steps, remember last displayed index)
  useEffect(() => {
    if (!customStepHistory || customStepHistory.length === 0) return;

    const interval = setInterval(() => {
      setDisplayedSteps((prev) => {
        if (lastDisplayedIndexRef.current < customStepHistory.length) {
          const nextStep = customStepHistory[lastDisplayedIndexRef.current];
          lastDisplayedIndexRef.current += 1;

          const updatedSteps = [...prev, nextStep];

          console.log("🧱 Showing step:", nextStep);

          if (
            nextStep
              .replace(/🧠|\s/g, "")
              .toLowerCase()
              .includes("constructioncomplete.")
          ) {
            console.log(
              "✅ Construction complete detected. Will trigger final message."
            );
            setReadyToShowFinalMessage(true);
          }

          return updatedSteps;
        } else {
          clearInterval(interval);
          return prev;
        }
      });
    }, 800);

    return () => clearInterval(interval);
  }, [customStepHistory]);

  // Show delayed bot message when ready and message exists
  useEffect(() => {
    
    if (readyToShowFinalMessage && delayedBotMsgRef.current) {
      console.log("💬 Displaying final bot message:", delayedBotMsgRef.current);
      setDisplayedSteps([]);
      setCustomStepHistory([]);
      setMessages((prev) => {
        const updated = [
          ...prev,
          {
            sender: "ai",
            text: delayedBotMsgRef.current || "No message generated.",
          },
        ];
        // Add scroll after DOM updates and clear delayedBotMsgRef
        setTimeout(() => {
          messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
          delayedBotMsgRef.current = "";
        }, 100);
        return updated;
      });
      setTrackingStep(null);
      setTrackingActive(false);
      setReadyToShowFinalMessage(false);
    }
  }, [readyToShowFinalMessage]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleSendMessage = async () => {
    if (!input.trim() && !selectedFile) return;

    const userMsg = { sender: "user", text: input || "Sent a file" };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);
    scrollToBottom();

    // Use delayedBotMsgRef for delayed message
    delayedBotMsgRef.current = "";

    try {
      setTrackingActive(true);
      setStepHistory([]);
      setDisplayedSteps([]);
      const response = await sendCopilotMessage(input, selectedFile);
      console.log("Response from backend:", response);

      let botMsg;
      if (response?.success && response?.response) {
        const res = response.response;

        if (
          Array.isArray(res.recommendations) &&
          res.recommendations.length > 0
        ) {
          const tickers = res.recommendations
            .map((rec) => rec.ticker)
            .filter((ticker) => typeof ticker === "string");

          if (tickers.length > 0) {
            setSuggestedStocks(tickers);
            setShowTrackDialog(true);
          }

          const detailedAnalyses = res.recommendations
            .map((rec) => {
              const t = rec.ticker;
              const analysis = rec.detailed_analysis;
              if (t && analysis) {
                return `${t}\n${analysis}`;
              }
              return null;
            })
            .filter(Boolean)
            .join("\n\n");

          botMsg =
            detailedAnalyses || tickers.map((t) => `**${t}**`).join(", ");
        } else if (res.natural_summary) {
          botMsg = res.natural_summary;
        } else {
          botMsg = JSON.stringify(res, null, 2);
        }

        if (
          res.portfolio_allocation &&
          Array.isArray(res.portfolio_allocation)
        ) {
          setSuggestedStocks(res.portfolio_allocation);
          setShowTrackDialog(true);
        }

        if (res.lifePlan) {
          botMsg = `🎯 HEDEF: ${res.lifePlan.goal}

💰 Estimated COST : ${res.lifePlan.estimatedCost}
💼 GENERAL SUMMERY OF PLAN : ${res.lifePlan.generalSummeryOfPlan}

📆 TIMELINE : ${res.lifePlan.timeline}

📊 MONTHLY PLAN:
${res.lifePlan.monthlyPlan}

✅ RECOMMENDATIONS:
${res.lifePlan.recommendations.map((r) => `- ${r}`).join("\n")}
          `;
        }

        if (res.transactions && Array.isArray(res.transactions)) {
          try {
            await saveTransactions(
              res.transactions,
              res.category_totals,
              res.card_limit
            );
            toast.success("Transactions saved to the database successfully!", {
              position: "top-right",
              autoClose: 5000,
              hideProgressBar: false,
              closeOnClick: true,
              pauseOnHover: true,
              draggable: true,
              progress: undefined,
            });
          } catch (saveError) {
            console.error("Error saving transactions:", saveError);
            toast.error("Error saving transactions. Please try again.", {
              position: "top-right",
              autoClose: 5000,
              hideProgressBar: false,
              closeOnClick: true,
              pauseOnHover: true,
              draggable: true,
              progress: undefined,
            });
          }
        }

        if (Array.isArray(res.URLs)) {
          const resolvedUrls = await Promise.all(
            res.URLs.map(async (url) => {
              try {
                const res = await resolveUrl(url);
                return res?.finalUrl || url;
              } catch (err) {
                console.error("resolveUrl threw:", JSON.stringify(err));
                return url;
              }
            })
          );
          setSources(resolvedUrls);
        } else {
          setSources(null);
        }
      } else {
        botMsg = "No response received.";
        setSources(null);
      }

      // Instead of sending the message here, assign to delayedBotMsgRef
      delayedBotMsgRef.current = botMsg;
    } catch (error) {
      if (error instanceof Error) {
        console.error("Error in handleSendMessage:", error.message);
      } else {
        console.error(
          "Unhandled error in handleSendMessage:",
          JSON.stringify(error, null, 2)
        );
      }
      setMessages((prev) => [
        ...prev,
        userMsg,
        { sender: "ai", text: "An error occurred. Please try again." },
      ]);
      setSources(null);
    } finally {
      setLoading(false);
      setSelectedFile(null);
      // No longer send delayedBotMsg here; handled in useEffect
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  const animateMessage = (prevUserMsg, botText) => {
    // Animation disabled temporarily
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) setSelectedFile(file);
    e.target.value = null;
  };

  const renderMessage = (msg, i) => (
    <Box
      key={i}
      sx={{
        display: "flex",
        justifyContent: msg.sender === "user" ? "flex-end" : "flex-start",
        gap: 2,
        alignItems: "flex-start",
      }}
    >
      {msg.sender === "ai" && (
        <Avatar sx={{ backgroundColor: colors.greenAccent[500] }}>
          <SmartToy fontSize="small" />
        </Avatar>
      )}
      <Box
        sx={{
          backgroundColor:
            msg.sender === "user"
              ? colors.greenAccent[500]
              : colors.primary[500],
          color: msg.sender === "user" ? "#fff" : colors.grey[100],
          padding: "12px 16px",
          borderRadius:
            msg.sender === "user" ? "18px 18px 0 18px" : "18px 18px 18px 0",
          maxWidth: "70%",
          maxHeight: "300px", // EKLENECEK
          overflowY: "auto", // EKLENECEK
        }}
      >
        <Typography sx={{ whiteSpace: "pre-wrap", wordBreak: "break-word" }}>
          {msg.text}
        </Typography>
      </Box>
      {msg.sender === "user" && (
        <Avatar sx={{ backgroundColor: colors.blueAccent[500] }}>
          <Person fontSize="small" />
        </Avatar>
      )}
    </Box>
  );

  return (
    <Box
      sx={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        height: "100vh",
        px: 2,
      }}
    >
      <Box
        sx={{
          width: "100%",
          maxWidth: "1100px",
          maxHeight: "700px",
          height: "90vh",
          borderRadius: 5,
          display: "flex",
          flexDirection: "column",
          overflow: "hidden",
          backgroundColor: colors.primary[800],
          position: "relative",
        }}
      >
        {/* Header */}
        <Box
          sx={{
            p: 2,
            display: "flex",
            alignItems: "center",
            borderBottom: `1px solid ${colors.primary[300]}`,
            gap: 2,
          }}
        >
          <Avatar sx={{ backgroundColor: colors.greenAccent[500] }}>
            <SmartToy />
          </Avatar>
          <Box>
            <Typography variant="h5">Finance Copilot</Typography>
            <Typography variant="body2">How can I assist you today?</Typography>
          </Box>
        </Box>
        {Array.isArray(sources) && sources.length > 0 && (
          <Button
            size="small"
            variant="outlined"
            sx={{
              position: "absolute",
              top: 12,
              right: 12,
              zIndex: 20,
              fontSize: "0.75rem",
              padding: "2px 8px",
              borderRadius: 2,
              color: colors.grey[100],
              borderColor: colors.grey[300],
              "&:hover": {
                borderColor: colors.greenAccent[500],
                color: colors.greenAccent[400],
              },
            }}
            onClick={() => setShowSources(!showSources)}
          >
            {showSources ? "Hide News Sources" : "Show News Sources"}
          </Button>
        )}

        {/* Messages */}
        <Box
          sx={{
            p: 2,
            flex: 1,
            overflowY: "auto",
            display: "flex",
            flexDirection: "column",
            gap: 2,
          }}
        >
          {messages.map(renderMessage)}
          {displayedSteps.map((step, idx) => (
            <Box
              key={idx}
              sx={{ display: "flex", justifyContent: "flex-start", px: 2 }}
            >
              <Typography variant="body2" color="text.secondary">
                🧠 {step}
              </Typography>
            </Box>
          ))}
          {loading && (
            <Box sx={{ display: "flex", justifyContent: "center", py: 1 }}>
              <CircularProgress size={24} />
            </Box>
          )}
          <Box ref={messagesEndRef} />
          {showSources && Array.isArray(sources) && sources.length > 0 && (
            <Box
              sx={{
                position: "absolute",
                right: 8,
                top: 80,
                backgroundColor: colors.primary[600],
                padding: 1,
                borderRadius: 2,
                boxShadow: 3,
                zIndex: 10,
                maxWidth: "90vw",
                maxHeight: "80vh",
                overflowX: "auto",
              }}
            >
              <Typography variant="subtitle1" sx={{ mb: 1 }}>
                News Sources:
              </Typography>
              {sources.map((url, index) => (
                <Tooltip
                  key={index}
                  title={
                    <Box sx={{ width: 360, height: 200, overflow: "hidden" }}>
                      <Box
                        sx={{
                          transform: "scale(0.4)",
                          transformOrigin: "top left",
                          width: "900px",
                          height: "500px",
                        }}
                      >
                        <iframe
                          src={url}
                          width="100%"
                          height="100%"
                          style={{ border: "none" }}
                          title={`iframe-${index}`}
                        />
                      </Box>
                    </Box>
                  }
                  arrow
                  placement="left"
                >
                  <Typography
                    variant="body2"
                    sx={{
                      color: colors.greenAccent[400],
                      cursor: "pointer",
                      "&:hover": { textDecoration: "underline" },
                      mb: 1,
                      wordBreak: "break-all",
                    }}
                    onClick={() => window.open(url, "_blank")}
                  >
                    {url}
                  </Typography>
                </Tooltip>
              ))}
            </Box>
          )}
        </Box>

        {/* Input */}
        <Box
          sx={{
            p: 2,
            borderTop: `1px solid ${colors.primary[300]}`,
          }}
        >
          {selectedFile && (
            <Box
              sx={{
                display: "flex",
                alignItems: "center",
                gap: 1,
                mb: 1,
                p: 1,
                borderRadius: 1,
                backgroundColor: colors.primary[500],
              }}
            >
              <Typography variant="body2" flex={1}>
                {selectedFile.name}
              </Typography>
              <IconButton onClick={() => setSelectedFile(null)} size="small">
                <Close />
              </IconButton>
            </Box>
          )}
          <Box sx={{ display: "flex", gap: 1, alignItems: "flex-end" }}>
            <Tooltip title="Upload File">
              <IconButton component="label">
                <AttachFile />
                <input
                  type="file"
                  hidden
                  onChange={handleFileSelect}
                  ref={fileInputRef}
                  accept=".pdf,.txt,.doc,.docx,.csv,.xls,.xlsx"
                />
              </IconButton>
            </Tooltip>
            <TextField
              fullWidth
              multiline
              maxRows={4}
              placeholder="Write your message here..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyPress}
              sx={{
                backgroundColor: colors.primary[500],
                borderRadius: 2,
                "& .MuiOutlinedInput-root": {
                  padding: "12px",
                  color: colors.grey[100],
                  "& fieldset": { border: "none" },
                },
              }}
            />
            <Button
              onClick={handleSendMessage}
              disabled={loading || (!input.trim() && !selectedFile)}
              variant="contained"
              sx={{
                minWidth: 48,
                height: 48,
                borderRadius: 2,
                backgroundColor: colors.greenAccent[500],
                "&:hover": { backgroundColor: colors.greenAccent[600] },
              }}
            >
              {loading ? <HourglassEmpty /> : <Send />}
            </Button>
          </Box>
        </Box>
      </Box>
      <Dialog open={showTrackDialog} onClose={() => setShowTrackDialog(false)}>
        <Box sx={{ p: 3, backgroundColor: colors.primary[300] }}>
          <Typography variant="h6" sx={{ mb: 2 }}>
            Do you want to track the following stocks?
          </Typography>
          <Typography sx={{ mb: 2 }}>{suggestedStocks.join(", ")}</Typography>
          <Box sx={{ display: "flex", justifyContent: "flex-end", gap: 1 }}>
            <Button onClick={() => setShowTrackDialog(false)}>Cancel</Button>
            <Button
              variant="contained"
              color="primary"
              onClick={async () => {
                try {
                  console.log("Saving suggested stocks:", suggestedStocks);
                  await saveUserStocks(suggestedStocks);
                  toast.success("Selected stocks are now being tracked!");
                } catch (error) {
                  console.error("Error saving stock suggestions:", error);
                  toast.error("Failed to save stock suggestions.");
                } finally {
                  setShowTrackDialog(false);
                }
              }}
            >
              Yes, Track
            </Button>
          </Box>
        </Box>
      </Dialog>
    </Box>
  );
};

export default Copilot;

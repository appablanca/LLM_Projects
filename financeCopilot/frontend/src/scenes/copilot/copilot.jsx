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
} from "@mui/material";
import {
  SmartToy,
  Person,
  Send,
  AttachFile,
  Close,
  HourglassEmpty,
} from "@mui/icons-material";
import { sendCopilotMessage } from "../../util/api";
import { tokens } from "../../theme";

const Copilot = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  const theme = useTheme();
  const colors = tokens(theme.palette.mode);

  useEffect(() => {
    // Add initial welcome message
    setMessages([
      {
        sender: "ai",
        text: "Hello! I'm your Finance Copilot. How can I help you today?"
      }
    ]);
  }, []);

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

    try {
      const response = await sendCopilotMessage(input, selectedFile);
      const botMsg = response?.response?.response || "No response received.";
      animateMessage(userMsg, botMsg);
    } catch (error) {
      animateMessage(userMsg, "An error occurred. Please try again.");
    } finally {
      setLoading(false);
      setSelectedFile(null);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  const animateMessage = (prevUserMsg, botText) => {
    let i = 0;
    const interval = setInterval(() => {
      if (i <= botText.length) {
        setMessages([
          ...messages,
          prevUserMsg,
          { sender: "ai", text: botText.slice(0, i) },
        ]);
        i++;
      } else {
        clearInterval(interval);
        scrollToBottom();
      }
    }, 15);
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
            <Typography variant="body2">
              How can I assist you today?
            </Typography>
          </Box>
        </Box>

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
          {loading && (
            <Box sx={{ display: "flex", justifyContent: "center", py: 1 }}>
              <CircularProgress size={24} />
            </Box>
          )}
          <div ref={messagesEndRef} />
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
    </Box>
  );
};

export default Copilot;

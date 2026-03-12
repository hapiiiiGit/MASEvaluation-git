import React, { useState } from "react";
import {
  Box,
  Button,
  TextField,
  Typography,
  Paper,
  IconButton,
  MenuItem,
  Grid,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
} from "@mui/material";
import { Add, Delete, Edit } from "@mui/icons-material";
import axios from "axios";

// Question types as per backend
const QUESTION_TYPES = [
  { value: "single_choice", label: "Single Choice" },
  { value: "multiple_choice", label: "Multiple Choice" },
  { value: "text", label: "Text" },
  { value: "rating", label: "Rating" },
  { value: "number", label: "Number" },
];

const emptyQuestion = {
  text: "",
  type: "single_choice",
  options: [""],
};

const SurveyBuilder = () => {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [questions, setQuestions] = useState([]);
  const [editingIndex, setEditingIndex] = useState(null);
  const [questionDraft, setQuestionDraft] = useState({ ...emptyQuestion });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  // Helper to reset question draft
  const resetQuestionDraft = () => {
    setQuestionDraft({ ...emptyQuestion });
    setEditingIndex(null);
  };

  // Add or update question
  const handleAddOrUpdateQuestion = () => {
    if (!questionDraft.text.trim()) {
      setMessage("Question text is required.");
      return;
    }
    if (
      (questionDraft.type === "single_choice" ||
        questionDraft.type === "multiple_choice") &&
      (!questionDraft.options || questionDraft.options.length < 2 || questionDraft.options.some(opt => !opt.trim()))
    ) {
      setMessage("Choice questions require at least 2 non-empty options.");
      return;
    }
    setMessage("");
    if (editingIndex !== null) {
      // Update
      const updated = [...questions];
      updated[editingIndex] = { ...questionDraft };
      setQuestions(updated);
    } else {
      // Add
      setQuestions([...questions, { ...questionDraft }]);
    }
    resetQuestionDraft();
  };

  // Edit question
  const handleEditQuestion = (idx) => {
    setEditingIndex(idx);
    setQuestionDraft({ ...questions[idx], options: questions[idx].options ? [...questions[idx].options] : [] });
  };

  // Remove question
  const handleRemoveQuestion = (idx) => {
    setQuestions(questions.filter((_, i) => i !== idx));
    if (editingIndex === idx) resetQuestionDraft();
  };

  // Handle option change for draft
  const handleOptionChange = (optIdx, value) => {
    const opts = questionDraft.options ? [...questionDraft.options] : [];
    opts[optIdx] = value;
    setQuestionDraft({ ...questionDraft, options: opts });
  };

  // Add option to draft
  const handleAddOption = () => {
    setQuestionDraft({
      ...questionDraft,
      options: questionDraft.options ? [...questionDraft.options, ""] : [""],
    });
  };

  // Remove option from draft
  const handleRemoveOption = (optIdx) => {
    const opts = questionDraft.options ? [...questionDraft.options] : [];
    opts.splice(optIdx, 1);
    setQuestionDraft({ ...questionDraft, options: opts });
  };

  // Handle question type change
  const handleQuestionTypeChange = (type) => {
    let opts = questionDraft.options;
    if (type === "single_choice" || type === "multiple_choice") {
      if (!opts || opts.length < 2) opts = ["", ""];
    } else {
      opts = undefined;
    }
    setQuestionDraft({ ...questionDraft, type, options: opts });
  };

  // Submit survey to backend
  const handleSubmitSurvey = async () => {
    if (!title.trim()) {
      setMessage("Survey title is required.");
      return;
    }
    if (questions.length === 0) {
      setMessage("At least one question is required.");
      return;
    }
    setLoading(true);
    setMessage("");
    try {
      // Replace with your actual JWT token retrieval logic
      const token = localStorage.getItem("token");
      const payload = {
        title,
        description,
        questions: questions.map((q) => ({
          text: q.text,
          type: q.type,
          options:
            q.type === "single_choice" || q.type === "multiple_choice"
              ? q.options
              : undefined,
        })),
      };
      const res = await axios.post(
        "/api/survey/",
        payload,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      setMessage("Survey created successfully!");
      setTitle("");
      setDescription("");
      setQuestions([]);
      resetQuestionDraft();
    } catch (err) {
      setMessage(
        err.response?.data?.detail ||
          "Failed to create survey. Please check your input and authentication."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          Create a New Survey
        </Typography>
        <Box sx={{ mb: 2 }}>
          <TextField
            label="Survey Title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            fullWidth
            required
            sx={{ mb: 2 }}
          />
          <TextField
            label="Description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            fullWidth
            multiline
            rows={2}
            sx={{ mb: 2 }}
          />
        </Box>
        <Divider sx={{ mb: 2 }} />
        <Typography variant="h6" gutterBottom>
          Questions
        </Typography>
        <List>
          {questions.map((q, idx) => (
            <ListItem key={idx} divider>
              <ListItemText
                primary={`${idx + 1}. ${q.text} (${QUESTION_TYPES.find(t => t.value === q.type)?.label || q.type})`}
                secondary={
                  (q.type === "single_choice" || q.type === "multiple_choice") && q.options
                    ? `Options: ${q.options.join(", ")}`
                    : null
                }
              />
              <ListItemSecondaryAction>
                <IconButton edge="end" aria-label="edit" onClick={() => handleEditQuestion(idx)}>
                  <Edit />
                </IconButton>
                <IconButton edge="end" aria-label="delete" onClick={() => handleRemoveQuestion(idx)}>
                  <Delete />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
        </List>
        <Divider sx={{ my: 2 }} />
        <Typography variant="subtitle1" gutterBottom>
          {editingIndex !== null ? "Edit Question" : "Add Question"}
        </Typography>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <TextField
              label="Question Text"
              value={questionDraft.text}
              onChange={(e) => setQuestionDraft({ ...questionDraft, text: e.target.value })}
              fullWidth
              required
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <TextField
              select
              label="Type"
              value={questionDraft.type}
              onChange={(e) => handleQuestionTypeChange(e.target.value)}
              fullWidth
            >
              {QUESTION_TYPES.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </TextField>
          </Grid>
        </Grid>
        {(questionDraft.type === "single_choice" || questionDraft.type === "multiple_choice") && (
          <Box sx={{ mt: 2, ml: 1 }}>
            <Typography variant="body2" gutterBottom>
              Options
            </Typography>
            {questionDraft.options &&
              questionDraft.options.map((opt, idx) => (
                <Box key={idx} sx={{ display: "flex", alignItems: "center", mb: 1 }}>
                  <TextField
                    value={opt}
                    onChange={(e) => handleOptionChange(idx, e.target.value)}
                    size="small"
                    sx={{ mr: 1, width: "60%" }}
                    placeholder={`Option ${idx + 1}`}
                  />
                  <IconButton
                    aria-label="delete-option"
                    onClick={() => handleRemoveOption(idx)}
                    disabled={questionDraft.options.length <= 2}
                  >
                    <Delete fontSize="small" />
                  </IconButton>
                </Box>
              ))}
            <Button
              variant="outlined"
              size="small"
              startIcon={<Add />}
              onClick={handleAddOption}
              sx={{ mt: 1 }}
            >
              Add Option
            </Button>
          </Box>
        )}
        <Box sx={{ mt: 2 }}>
          <Button
            variant="contained"
            color="primary"
            onClick={handleAddOrUpdateQuestion}
            sx={{ mr: 2 }}
          >
            {editingIndex !== null ? "Update Question" : "Add Question"}
          </Button>
          {editingIndex !== null && (
            <Button variant="outlined" color="secondary" onClick={resetQuestionDraft}>
              Cancel
            </Button>
          )}
        </Box>
        <Divider sx={{ my: 3 }} />
        <Box sx={{ mt: 2 }}>
          <Button
            variant="contained"
            color="success"
            onClick={handleSubmitSurvey}
            disabled={loading}
            size="large"
          >
            {loading ? "Submitting..." : "Submit Survey"}
          </Button>
        </Box>
        {message && (
          <Typography color={message.includes("success") ? "success.main" : "error"} sx={{ mt: 2 }}>
            {message}
          </Typography>
        )}
      </Paper>
    </Container>
  );
};

export default SurveyBuilder;
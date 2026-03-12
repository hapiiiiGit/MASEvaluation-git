import React from "react";
import { Box, TextField, Typography, Divider, Button, List, ListItem, ListItemText } from "@mui/material";
import { Download as DownloadIcon, FilterList as FilterListIcon } from "@mui/icons-material";

/**
 * SegmentationSidebar component for dashboard.
 * Provides controls for segmenting/filtering data (facebook_id, email, contact_id, stage)
 * and includes export button. Uses MUI and Tailwind CSS.
 */
const stages = [
  "appointmentscheduled",
  "qualifiedtobuy",
  "presentation scheduled",
  "decisionmakerboughtin",
  "contractsent",
  "closedwon",
  "closedlost",
];

const SegmentationSidebar = ({
  segmentation,
  onChange,
  onExport,
}) => {
  // Handlers for input changes
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    onChange({ [name]: value });
  };

  return (
    <aside className="w-full md:w-64 bg-white border-r border-gray-200 p-6 flex flex-col gap-6 min-h-[600px]">
      <Typography variant="h6" className="font-bold text-gray-700 mb-2 flex items-center gap-2">
        <FilterListIcon fontSize="small" /> Segmentation
      </Typography>
      <Divider className="mb-4" />

      <Box className="flex flex-col gap-4">
        <TextField
          label="Facebook ID"
          name="facebook_id"
          value={segmentation.facebook_id}
          onChange={handleInputChange}
          size="small"
          variant="outlined"
          fullWidth
        />
        <TextField
          label="Email"
          name="email"
          value={segmentation.email}
          onChange={handleInputChange}
          size="small"
          variant="outlined"
          fullWidth
        />
        <TextField
          label="Contact ID"
          name="contact_id"
          value={segmentation.contact_id}
          onChange={handleInputChange}
          size="small"
          variant="outlined"
          fullWidth
        />
        <TextField
          label="Deal Stage"
          name="stage"
          value={segmentation.stage}
          onChange={handleInputChange}
          size="small"
          variant="outlined"
          fullWidth
          select
          SelectProps={{
            native: true,
          }}
        >
          <option value=""></option>
          {stages.map((stage) => (
            <option key={stage} value={stage}>
              {stage}
            </option>
          ))}
        </TextField>
      </Box>

      <Divider className="my-4" />

      <Typography variant="subtitle1" className="font-semibold text-gray-600 mb-2">
        Quick Export
      </Typography>
      <List dense>
        <ListItem disablePadding>
          <Button
            variant="contained"
            color="primary"
            startIcon={<DownloadIcon />}
            fullWidth
            onClick={() => onExport("metrics")}
            sx={{ mb: 1, textTransform: "none" }}
          >
            Export Metrics
          </Button>
        </ListItem>
        <ListItem disablePadding>
          <Button
            variant="contained"
            color="secondary"
            startIcon={<DownloadIcon />}
            fullWidth
            onClick={() => onExport("contacts")}
            sx={{ mb: 1, textTransform: "none" }}
          >
            Export Contacts
          </Button>
        </ListItem>
        <ListItem disablePadding>
          <Button
            variant="contained"
            color="success"
            startIcon={<DownloadIcon />}
            fullWidth
            onClick={() => onExport("deals")}
            sx={{ textTransform: "none" }}
          >
            Export Deals
          </Button>
        </ListItem>
      </List>
    </aside>
  );
};

export default SegmentationSidebar;
# Dashboard Upload Zones - User Guide

## Visual Layout

```
┌─────────────────────────────────────────────────────────────────┐
│                    TAX FILING DASHBOARD                         │
├─────────────────────────────────────────────────────────────────┤
│                      [Status Cards]                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Tax Year    │  │ Est. Tax     │  │ Documents    │          │
│  │  2024-25     │  │ ₹45,000      │  │ 0/3 Uploaded │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
├─────────────────────────────────────────────────────────────────┤
│                    UPLOAD TAX DOCUMENTS                         │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 📤 Form 16 - Part A                                     │   │
│  │    Salary and TDS information                           │   │
│  │                                                         │   │
│  │    [Browse File]                                        │   │
│  │    PDF, JSON, JPG, PNG (Max 10MB)                       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 📤 Form 16 - Part B                                     │   │
│  │    Deductions and loss details                          │   │
│  │                                                         │   │
│  │    [Browse File]                                        │   │
│  │    PDF, JSON, JPG, PNG (Max 10MB)                       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 📤 Form AIS                                             │   │
│  │    Interest income and other sources                    │   │
│  │                                                         │   │
│  │    [Browse File]                                        │   │
│  │    PDF, JSON, JPG, PNG (Max 10MB)                       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ [Download Report]     [UPLOAD ALL DOCS FIRST] (disabled)│   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Upload States

### 1. Empty (Initial State)
```
┌──────────────────────────────────┐
│            📤 UPLOAD             │
│                                  │
│  Form 16 - Part A                │
│  Salary and TDS information      │
│                                  │
│      [Browse File]               │
│  PDF, JSON, JPG, PNG (Max 10MB)  │
└──────────────────────────────────┘
```
- Border: Gray dashed
- Icon: Upload icon
- Color: Gray text

### 2. Uploading (In Progress)
```
┌──────────────────────────────────┐
│         🔄 UPLOADING             │
│                                  │
│  Uploading...                    │
│  ████████░░░░░░░░░░░░░░░░░░░░   │
│  45%                             │
└──────────────────────────────────┘
```
- Border: Blue (drag-over state)
- Background: Light blue
- Icon: Spinning upload icon
- Progress bar: Animated blue

### 3. Completed (Success)
```
┌──────────────────────────────────┐
│     ✓ UPLOAD COMPLETE            │
│                                  │
│            ✓                     │
│                                  │
│  ┌──────────────────────────────┐│
│  │📄 form16a.pdf          [✕]   ││
│  └──────────────────────────────┘│
└──────────────────────────────────┘
```
- Border: Green dashed
- Background: Light green
- Icon: Green checkmark
- File display: Shows file name with remove button (X)

## Status Card Behavior

### Status During Upload

When 0 files uploaded:
```
Document Status
──────────────
○ Form 16-A     (empty circle)
○ Form 16-B     (empty circle)
○ Form AIS      (empty circle)

0/3 uploaded (orange text)
```

When 1 file uploaded:
```
Document Status
──────────────
✓ Form 16-A     (green checkmark)
○ Form 16-B     (empty circle)
○ Form AIS      (empty circle)

1/3 uploaded (orange text)
```

When 2 files uploaded:
```
Document Status
──────────────
✓ Form 16-A     (green checkmark)
✓ Form 16-B     (green checkmark)
○ Form AIS      (empty circle)

2/3 uploaded (orange text)
```

When all 3 uploaded:
```
Document Status
──────────────
✓ Form 16-A     (green checkmark)
✓ Form 16-B     (green checkmark)
✓ Form AIS      (green checkmark)

✓ All documents ready (green text)
```

## Button State

### Disabled (Before all uploads)
```
┌──────────────────────────────────────┐
│  Download Report  │  Upload All Docs  │
│                   │     First (gray)  │
└──────────────────────────────────────┘
```
- Color: Gray background
- Text: "Upload All Documents First"
- Cursor: not-allowed
- Click: No action

### Enabled (After all uploads)
```
┌──────────────────────────────────────┐
│  Download Report  │  Compute Tax (✓)  │
│                   │   (green enabled)  │
└──────────────────────────────────────┘
```
- Color: Green background (#10B981)
- Text: "Compute Tax"
- Cursor: pointer
- Click: Proceeds to calculation

## Drag & Drop Behavior

### While Dragging Over a Zone
```
┌──────────────────────────────────┐
│  Drop file here                  │
│                                  │
│  Form 16 - Part A                │  ← Border turns blue
│  (light blue background)         │  ← Background changes
│                                  │
│      [Browse File]               │  ← Upload icon turns blue
└──────────────────────────────────┘
```

After dropping file:
→ Automatically transitions to "Uploading" state

## File Removal

When file is uploaded, users can remove it:
```
✓ Upload Complete
        ✓
┌──────────────────────────────────┐
│📄 form16a.pdf              [✕]   │  ← Click X to remove
└──────────────────────────────────┘
```

After clicking X:
→ Zone returns to "Empty" state
→ Can upload a new file
→ Status card updates (count decreases)
→ Button disables if needed

## Key Features

✅ **Independent Zones**
- Each document is handled separately
- No cross-contamination of states
- Can upload in any order

✅ **Visual Feedback**
- Color changes indicate state
- Progress bar shows upload status
- Checkmarks confirm completion

✅ **Clear Status**
- Status card shows real-time progress
- Count displayed (X/3 uploaded)
- Ready indicator when complete

✅ **Button Control**
- Disabled until all required files present
- Clear message about requirements
- Enables automatically when ready

✅ **User-Friendly**
- Drag-and-drop support
- Click to browse alternative
- Easy file removal with X button

## Common Workflows

### Workflow 1: Upload All Three
1. Drag Form 16-A file → Zone 1 shows progress → Complete
2. Drag Form 16-B file → Zone 2 shows progress → Complete
3. Drag Form AIS file → Zone 3 shows progress → Complete
4. Status shows "✓ All documents ready"
5. "Compute Tax" button turns green and enables
6. Click "Compute Tax" to proceed

### Workflow 2: Fix a Wrong File
1. Notice wrong file uploaded to Form 16-A
2. Click X button to remove it
3. Status card updates to "1/3 uploaded"
4. Button disables again
5. Upload correct file to Form 16-A zone
6. All three complete again
7. Button enables for computation

### Workflow 3: Partial Upload (Can't Proceed)
1. Upload Form 16-A → 1/3 uploaded
2. Upload Form 16-B → 2/3 uploaded
3. Forget to upload Form AIS
4. Try to click "Compute Tax" → Button is disabled
5. Clear message says "Upload All Documents First"
6. User remembers to upload Form AIS
7. Zone 3 complete → All 3/3 ready
8. Button enables → Can proceed

## Technical Details

### Upload Zone Props
```typescript
interface UploadZoneProps {
  title: string;              // "Form 16 - Part A"
  description: string;        // "Salary and TDS info"
  state: DocumentUpload;      // Current upload state
  setState: (value) => void;  // Update state
  isDragging: boolean;        // Drag-over state
  setIsDragging: (v) => void; // Update drag state
  inputId: string;            // "form16-a" etc
}
```

### Document State
```typescript
interface DocumentUpload {
  fileName: string | null;
  status: 'empty' | 'uploading' | 'completed' | 'error';
  progress: number;  // 0-100
}
```

## Responsive Behavior

- **Desktop**: All three zones visible, stacked vertically
- **Tablet**: Same layout, slightly smaller zones
- **Mobile**: Zones take full width, easily tappable

---

This guide explains the complete behavior of the new three-zone upload system!

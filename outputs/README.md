# 📁 Output Directory

This folder stores the generated outputs from the **iMarker Detector Standalone** program. It serves as a centralized location for logging visualizations, debug results, intermediate artifacts, and final detections.

## 🏷️ File Naming Convention

All saved outputs follow a structured naming scheme to help trace back to the specific run configuration:

```
YYYYMMDD_HHMMSS_<variant>.<ext>
```

`<ext>` refers to the file extension, including `png` and `jpg`. Also, `<variant>` shows the sensor-algorithm pair variant used during execution, including:

| Variant    | Description                          |
| ---------- | ------------------------------------ |
| `offimg`   | Offline static frame (RGB camera)    |
| `offimguv` | Offline static frame (UV camera)     |
| `offvid`   | Offline video-based processing       |
| `usb`      | USB dual-vision RGB camera setup     |
| `usbuv`    | USB dual-vision UV camera setup      |
| `ids`      | IDS dual-vision camera setup         |
| `rs`       | RealSense single-vision camera setup |

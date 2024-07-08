# Upgrading guide

## 2.0.0

- Replace `from PekatVisionSDK.pekat_vision_instance import ...` with import from the toplevel module: `from PekatVisionSDK import ...`
- Replace `context = Instance.analyze(..., response_type="context")` with `context = Instance.analyze(..., response_type="context").context`

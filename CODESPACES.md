# Run Traffic Flow in GitHub Codespaces

1. Open the repository on GitHub. Select **Code → Codespaces → Create codespace on main**.
2. Wait for the container and dependency installation to finish. The app starts automatically on port **8050**, including after a Codespace restart.
3. In the Explorer, right-click the **models** folder and choose **Upload**. Select your local `C:\ai\yolo_11\best-4.pt`. Wait for the upload to finish. Weights are not included in the public repository.
4. Open the **Ports** panel and select **Open in Browser** for port 8050. The interface checks for the model every 10 seconds. Choose an image, video, or camera input once the class selector loads.

The forwarded port is private by default. Keep it private for your own testing. If you deliberately want to share the demonstration, change its visibility in the Ports panel; anyone with access to that link can submit images for inference.

Camera input uses the visitor's browser camera, not a camera on the cloud server. Open the forwarded HTTPS URL in a browser tab and grant camera permission when prompted.

## Troubleshooting

- **Model not found:** confirm the filename is exactly `models/best-4.pt` and the upload has finished. Model files must be supplied separately for each new Codespace.
- **No forwarded page:** open Ports and forward port 8050. Check `.runtime/server.log` in the Explorer for startup errors.
- **Restart the server:** run `.venv/bin/python .devcontainer/start.py` in the Codespace terminal. It checks for an existing healthy server first.
- **Tests:** run `.venv/bin/python -m unittest test_app.py` in the Codespace terminal.

Codespaces is a development/demo environment, not continuous production hosting. The URL works while the Codespace runs. GitHub stops idle Codespaces; compute and storage use count toward your account's allowances and may be billed according to your plan. Stop the Codespace when finished.

References: [Forwarded ports](https://docs.github.com/en/codespaces/developing-in-a-codespace/forwarding-ports-in-your-codespace), [Codespace lifecycle](https://docs.github.com/en/codespaces/about-codespaces/understanding-the-codespace-lifecycle).

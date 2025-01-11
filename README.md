Forked from [claude-computer-use-macos](https://github.com/PallavAg/claude-computer-use-macos). Added a couple of changes to optimize the computer use.

## Installation and Setup

1. **Clone the repository:**


2. **Create a virtual environment + install dependencies:**
Needs Python 3.12 installed
   ```bash
   python3.12 -m venv venv
   source venv/bin/activate
   pip3.12 install -r requirements.txt
   ```

3. **Set your Anthropic API key as an environment variable:**

   ```bash
   export ANTHROPIC_API_KEY="CLAUDE_API_KEY"
   ```

   Replace `CLAUDE_API_KEY` with your actual Anthropic API key. You find yours [here](https://console.anthropic.com/settings/keys).

4. **Grant Accessibility Permissions:**

   The script uses `pyautogui` to control mouse and keyboard events. On MacOS, you need to grant accessibility permissions. These popups should show automatically the first time you run the script so you can skip this step. But to manually provide permissions:

   - Go to **System Preferences** > **Security & Privacy** > **Privacy** tab.
   - Select **Accessibility** from the list on the left.
   - Add your terminal application or Python interpreter to the list of allowed apps.

## Usage

You can run the script by passing the instruction directly via the command line or by editing the `main.py` file.

**Example using command line instruction:**

```bash
python3.12 main.py 'Open Safari and look up Magic Ajji'
```

Replace `'Open Safari and look up Magic Ajji'` with your desired instruction.

**Note:** If you do not provide an instruction via the command line, the script will use the default instruction specified in `main.py`. You can edit `main.py` to change this default instruction.

## Exiting the Script

You can quit the script at any time by pressing `Ctrl+C` in the terminal.

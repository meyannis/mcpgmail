# Gmail MCP Server

<div align="center">

A powerful Model Context Protocol (MCP) server that enables Claude AI to directly interact with Gmail.

![Gmail MCP](https://img.shields.io/badge/Gmail-MCP-red?style=for-the-badge&logo=gmail)
[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE) 
![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg?style=for-the-badge&logo=python)
</div>

## 📖 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Quick Start](#quick-start)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Set up Google Cloud and OAuth credentials](#set-up-google-cloud-and-oauth-credentials)
  - [First Run and Authentication](#first-run-and-authentication)
  - [Configure Claude Desktop](#configure-claude-desktop)
- [Available Tools](#available-tools)
- [Usage Examples](#usage-examples)
- [Advanced Configuration](#advanced-configuration)
  - [Environment Variables](#environment-variables)
  - [SSE Server Mode](#sse-server-mode)
- [Documentation](#documentation)
- [Security Considerations](#security-considerations)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## 📋 Overview

The Gmail MCP Server is a comprehensive implementation that enables AI assistants like Claude to directly interact with Gmail through natural language. It exposes a rich set of tools for email management, enabling seamless integration between conversational AI and your inbox.

### 💡 Key Features

- **Complete Email Management**
  - Send plain text and HTML emails with attachments
  - Read emails with proper parsing of complex message structures
  - Search your inbox with Gmail's powerful query syntax
  - Create and update draft emails
  - Manage labels, read/unread status, and trash
  - Perform batch operations on multiple emails

- **Advanced Integration**
  - Modern Python codebase with async/await pattern
  - Comprehensive error handling and recovery
  - Detailed progress reporting
  - Secure OAuth authentication flow
  - Multiple transport modes (STDIO and SSE)
  - Support for different deployment scenarios

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- A Google Cloud project with the Gmail API enabled
- OAuth 2.0 credentials for the Gmail API

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/gmail-mcp-server.git
   cd gmail-mcp-server
   ```

2. **Set up a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Google Cloud and OAuth credentials**
   
   Visit the [Google Cloud Console](https://console.cloud.google.com/) to:
   - Create a new project
   - Enable the Gmail API
   - Set up OAuth consent screen
   - Create OAuth Client ID credentials (Desktop application)
   - Download credentials as `credentials.json` in project root

### First Run and Authentication

Run the server once to authenticate:

```bash
python gmail_server.py
```

This will open a browser window asking you to authenticate with your Google account. After authentication, a `token.json` file will be created and saved for future use.

### Configure Claude Desktop

1. Edit your Claude Desktop configuration file:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. Add the Gmail MCP server to the configuration:

   ```json
   {
     "mcpServers": {
       "gmail": {
         "command": "python",
         "args": [
           "/absolute/path/to/gmail-mcp-server/gmail_server.py"
         ]
       }
     }
   }
   ```

3. Save the file and restart Claude Desktop

**Note:** Replace `"/absolute/path/to/gmail-mcp-server/gmail_server.py"` with the actual absolute path to the `gmail_server.py` file in your cloned repository.

## 🧰 Available Tools

The Gmail MCP Server exposes the following tools to Claude:

### Email Sending
- `send_email` - Send basic emails with text/HTML content
- `send_email_with_attachment` - Send emails with file attachments
- `send_email_with_multiple_attachments` - Send emails with multiple attachments

### Email Reading
- `read_email` - Read the content of a specific email by ID
- `get_unread_emails` - Get a list of unread emails
- `get_important_emails` - Get emails marked as important
- `get_emails_with_attachments` - Get emails that have attachments
- `get_recent_emails` - Get emails from the last X days

### Email Search and Organization
- `search_emails` - Search emails using Gmail's query syntax
- `get_email_labels` - List all Gmail labels/folders
- `create_email_label` - Create a new label
- `delete_email_label` - Delete an existing label
- `label_email` - Apply a label to an email
- `remove_email_label` - Remove a label from an email

### Email Status Management
- `mark_as_read` - Mark an email as read
- `mark_as_unread` - Mark an email as unread
- `delete_email` - Move an email to trash

### Draft Management
- `create_email_draft` - Create a new draft email
- `update_email_draft` - Update an existing draft
- `list_email_drafts` - List available drafts
- `send_draft` - Send an existing draft

### Batch Operations
- `batch_apply_label` - Apply a label to multiple emails
- `batch_delete_emails` - Move multiple emails to trash

### Account Information
- `get_email_profile` - Get Gmail profile information
- `summarize_recent_emails` - Create a summary of recent emails

## 💬 Usage Examples

Here are some example prompts for Claude:

```
Send an email to john@example.com with the subject "Project Update" and let them know we're still on track for the deadline next week.
```

```
Search my inbox for any emails from Bank of America in the last month and summarize them for me.
```

```
Find all unread emails from my boss and create a summary of any action items mentioned in them.
```

```
Draft an email to the team about the upcoming meeting on Thursday at 2pm. Remind everyone to prepare their weekly updates.
```

## 🔧 Advanced Configuration

### Environment Variables

The server supports multiple environment variables for customization:

| Variable | Description |
|----------|-------------|
| `GMAIL_TOKEN_PATH` | Custom path to store OAuth token |
| `GMAIL_CREDENTIALS_PATH` | Custom path to OAuth credentials |
| `GOOGLE_CLIENT_ID` | OAuth client ID (alternative to credentials file) |
| `GOOGLE_CLIENT_SECRET` | OAuth client secret (alternative to credentials file) |
| `MCP_PORT` | Port for SSE transport (default: 3000) |
| `DEBUG` | Enable debug mode (`true` or `false`) |

### SSE Server Mode

The server can be run in SSE (Server-Sent Events) mode for HTTP-based integration:

```bash
python gmail_server.py --sse [port]
```

This starts the server on the specified port (default: 3000), making it accessible via HTTP.

## 📚 Documentation

- [MCP Specification](https://spec.modelcontextprotocol.io) - Learn about the Model Context Protocol
- [Gmail API Documentation](https://developers.google.com/gmail/api/guides) - Reference for Gmail API capabilities
- [Google Cloud OAuth](https://developers.google.com/identity/protocols/oauth2) - Details on authentication flows

## 🔒 Security Considerations

- The server uses OAuth 2.0 for secure Gmail API authentication
- All actions run locally on your machine - emails never pass through third-party servers
- Authentication tokens are stored locally and can be revoked at any time
- The server requires local file access only for reading attachments
- Claude always asks for confirmation before sending or deleting emails

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google for the Gmail API
- Anthropic for Claude and the Model Context Protocol
- Contributors to the Python Gmail API client libraries

---

<div align="center">
Made with ❤️ for the MCP and Claude community
</div>

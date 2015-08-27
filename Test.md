
# Test case for creating a connection

## Feature: Connection to server

### Scenario: Server accepts incoming connections
Given the server is up and running
When the server is telnetted to
Then the server answers and provides access to ftp commands
and the user can logout with 'quit' command

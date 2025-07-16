#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <unistd.h>
#include <nats/nats.h>
#include <curl/curl.h>
#include <glib.h>
#include "helpers.h"

volatile sig_atomic_t stop = 0;

void handle_sigint(int sig)
{
    stop = 1;
}

int main(int argc, char **argv)
{
    char plain_text_credentials[BUFFER_SIZE];
    char filename[] = "/secrets/nats-credentials.txt";
    char nats_server_url[] = "nats://nats.mnq.fr-par.scaleway.com:4222";
    char cwd[PATH_MAX];
    char filepath[PATH_MAX + sizeof(filename)];
    char *nats_subject = NULL;
    natsConnection *conn = NULL;
    natsStatus s;
    natsOptions *opts = NULL;

    // Read input arguments.
    if (argc != 4) {
        fprintf(stderr, "[ERROR] Usage: %s <vehicle_id> <topic> <interval>, with interval > 0\n", argv[0]);
        return 1; // Expecting exactly three arguments
    }
    char *vehicle_id = argv[1];
    char *topic = argv[2];
    int interval = atoi(argv[3]); // The interval between two consecutive signals
    if (interval <= 0) {
        fprintf(stderr, "[ERROR] Usage: %s <vehicle_id> <topic> <interval>, with interval > 0\n", argv[0]);
        return 1; // Invalid interval
    }

    // Create the NATS subject with this format: "vehicle.<vehicle_id>.<topic>".
    nats_subject = build_nats_subject(vehicle_id, topic);

    // Calculate the absolute path of the file where the credentials will be stored.
    getcwd(cwd, sizeof(cwd));
    snprintf(filepath, sizeof(filepath), "%s/%s", cwd, filename);

    // Preemptively retrieve the NATS credentials from Scaleway Secret Manager
    // and store them in a file, even though they might already be there from
    // a previous run of the program. This makes sure that the credentials are
    // always up-to-date.
    int credentials_size = get_plain_text_credentials(plain_text_credentials);
    if (credentials_size == 0) {
        fprintf(stderr, "[ERROR] Data producer failed to retrieve NATS credentials.\n");
        goto cleanup;
    }
    int ok = write_credentials_to_file(plain_text_credentials, filepath, credentials_size);
    if (ok) {
        printf("[DEBUG] Data producer saved NATS credentials.\n", filename);
    } else {
        fprintf(stderr, "[ERROR] Data producer failed to open file for writing credentials.\n");
        goto cleanup;
    }

    // Initialize NATS options structure.
    s = natsOptions_Create(&opts);
    if (s != NATS_OK) goto cleanup;
    
    // Set server URL.
    s = natsOptions_SetURL(opts, nats_server_url);
    if (s != NATS_OK) goto cleanup;
    
    // Set credentials file path.
    s = natsOptions_SetUserCredentialsFromFiles(opts, filepath, NULL);
    if (s != NATS_OK) goto cleanup;
    
    // Connect to the NATS server.
    s = natsConnection_Connect(&conn, opts);
    if (s != NATS_OK) goto cleanup;

    // Setup signal handler to handle SIGINT (Ctrl+C), so that the program shuts down gracefully.
    signal(SIGINT, handle_sigint);

    // Loop to send signals at the specified interval until SIGINT is received.
    while (!stop) {
        double value = get_random_value(0.0, 100.0); // Generate a random value between 0 and 100
        char string_value[32];
        snprintf(string_value, sizeof(string_value), "%.2f", value); // Cast to a string with 2 decimal digits

        // Send the signal to the appropriate subject for this vehicle.
        s = natsConnection_PublishString(conn, nats_subject, string_value);
        printf("%s: %s\n", nats_subject, string_value);
        if (s != NATS_OK) goto cleanup;

        sleep(interval); // Sleep for the specified interval
    }

    printf("[DEBUG] Data producer received a shutdown request. Shutting down...\n");
    goto cleanup;

    cleanup: return nats_Cleanup(conn, opts, s);
}

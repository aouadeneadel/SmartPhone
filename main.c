#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <unistd.h>

#define BUFFER_SIZE 4096

// ================= GLPI CONFIG =================
#define GLPI_URL "https://abn.fr33.glpi-network.cloud/apirest.php"
#define GLPI_APP_TOKEN "9S83SRUGnhUnrsxKZCZ11iL4D3Qn1YrIE4vytgwV"
#define GLPI_USER_TOKEN "huf3TwNjWKXTBMRO36gO90bL7JNHizcK3HARrx6N"
// ===============================================

typedef enum {
    STATUS_ERROR = -1,
    STATUS_NOT_FOUND = 0,
    STATUS_FOUND = 1,
    STATUS_UNAUTHORIZED = 2
} DeviceStatus;

typedef struct {
    char model[BUFFER_SIZE];
    char brand[BUFFER_SIZE];
    char android_version[BUFFER_SIZE];
    char sdk_version[BUFFER_SIZE];
    char serial[BUFFER_SIZE];
    char battery_level[BUFFER_SIZE];
    char inventory_number[BUFFER_SIZE];
} DeviceInfo;

bool run_command(const char *cmd) {
    int result = system(cmd);
    return result == 0;
}

bool run_command_full(const char *cmd, char *output, size_t size) {
    FILE *fp = popen(cmd, "r");
    if (!fp) return false;

    output[0] = '\0';
    size_t len = 0;

    while (fgets(output + len, size - len, fp)) {
        len = strlen(output);
        if (len >= size - 1) break;
    }

    pclose(fp);
    return len > 0;
}

void trim_newline(char *str) {
    str[strcspn(str, "\r\n")] = 0;
}

void print_success(const char *m){ printf("\033[1;32m✓ %s\033[0m\n", m); }
void print_error(const char *m){ printf("\033[1;31m✗ %s\033[0m\n", m); }
void print_info(const char *m){ printf("\033[1;34mℹ %s\033[0m\n", m); }

DeviceStatus check_adb() {
    FILE *fp = popen("adb devices 2>&1", "r");
    if (!fp) return STATUS_ERROR;

    char line[BUFFER_SIZE];
    bool found = false;
    bool unauthorized = false;

    while (fgets(line, sizeof(line), fp)) {
        if (strstr(line, "unauthorized")) unauthorized = true;
        if (strstr(line, "\tdevice")) found = true;
    }

    pclose(fp);

    if (unauthorized) return STATUS_UNAUTHORIZED;
    return found ? STATUS_FOUND : STATUS_NOT_FOUND;
}

bool get_device_info_adb(DeviceInfo *info) {
    if (!info) return false;

    bool ok = true;

    ok &= run_command_full("adb shell getprop ro.product.model", info->model, BUFFER_SIZE);
    ok &= run_command_full("adb shell getprop ro.product.brand", info->brand, BUFFER_SIZE);
    ok &= run_command_full("adb shell getprop ro.build.version.release", info->android_version, BUFFER_SIZE);
    ok &= run_command_full("adb shell getprop ro.build.version.sdk", info->sdk_version, BUFFER_SIZE);
    ok &= run_command_full("adb shell getprop ro.serialno", info->serial, BUFFER_SIZE);
    ok &= run_command_full("adb shell dumpsys battery | grep level | awk '{print $2}'", info->battery_level, BUFFER_SIZE);

    trim_newline(info->model);
    trim_newline(info->brand);
    trim_newline(info->android_version);
    trim_newline(info->sdk_version);
    trim_newline(info->serial);
    trim_newline(info->battery_level);

    if (strlen(info->serial) == 0)
        strcpy(info->serial, "Non disponible");

    return ok;
}

void factory_reset_adb() {

    DeviceStatus status = check_adb();

    if (status == STATUS_UNAUTHORIZED) {
        print_error("Telephone non autorise (verifier ecran)");
        return;
    }

    if (status != STATUS_FOUND) {
        print_error("Aucun appareil detecte");
        return;
    }

    char confirm[16];
    print_info("ATTENTION : Retour aux valeurs d'usine.");
    printf("Confirmer (OUI pour valider): ");
    if (!fgets(confirm, sizeof(confirm), stdin)) return;
    trim_newline(confirm);

    if (strcmp(confirm, "OUI") != 0) {
        print_info("Operation annulee.");
        return;
    }

    if (run_command("adb reboot recovery")) {
        print_success("Recovery lance.");
        print_info("Selectionner 'Wipe data / factory reset' sur le telephone.");
    } else {
        print_error("Echec du reboot recovery.");
    }
}

void factory_reset_fastboot() {

    char confirm[16];
    print_info("ATTENTION : Reset via Fastboot.");
    printf("Confirmer (OUI pour valider): ");
    if (!fgets(confirm, sizeof(confirm), stdin)) return;
    trim_newline(confirm);

    if (strcmp(confirm, "OUI") != 0) {
        print_info("Operation annulee.");
        return;
    }

    print_info("Passage en mode bootloader...");
    if (!run_command("adb reboot bootloader")) {
        print_error("Impossible de passer en bootloader.");
        return;
    }

    sleep(5);

    char buffer[BUFFER_SIZE];
    if (!run_command_full("fastboot devices", buffer, BUFFER_SIZE) ||
        strlen(buffer) < 3) {
        print_error("Aucun appareil fastboot detecte.");
        return;
    }

    print_info("Effacement des donnees (fastboot -w)...");
    if (!run_command("fastboot -w")) {
        print_error("Echec du wipe.");
        return;
    }

    print_info("Redemarrage appareil...");
    if (run_command("fastboot reboot"))
        print_success("Reset termine.");
    else
        print_error("Echec reboot.");
}

bool get_glpi_session(char *session_token) {

    char cmd[BUFFER_SIZE];
    char response[BUFFER_SIZE];

    snprintf(cmd, sizeof(cmd),
        "curl -s -X GET \"%s/initSession\" "
        "-H \"Content-Type: application/json\" "
        "-H \"App-Token: %s\" "
        "-H \"Authorization: user_token %s\"",
        GLPI_URL, GLPI_APP_TOKEN, GLPI_USER_TOKEN);

    if (!run_command_full(cmd, response, sizeof(response)))
        return false;

    sscanf(response, "{\"session_token\":\"%255[^\"]\"}", session_token);
    return strlen(session_token) > 0;
}

void create_glpi_ticket() {

    DeviceStatus status = check_adb();

    if (status == STATUS_UNAUTHORIZED) {
        print_error("Telephone non autorise (verifier ecran)");
        return;
    }

    if (status != STATUS_FOUND) {
        print_error("Aucun appareil detecte");
        return;
    }

    DeviceInfo info;
    if (!get_device_info_adb(&info)) {
        print_error("Impossible de recuperer infos appareil");
        return;
    }

    ask_inventory_number(&info);

    char session_token[256] = {0};

    print_info("Connexion GLPI...");
    if (!get_glpi_session(session_token)) {
        print_error("Echec session GLPI");
        return;
    }

    print_success("Session OK");

    char cmd[BUFFER_SIZE];

    snprintf(cmd, sizeof(cmd),
        "curl -s -X POST \"%s/Ticket\" "
        "-H \"Content-Type: application/json\" "
        "-H \"App-Token: %s\" "
        "-H \"Session-Token: %s\" "
        "-d '{"
        "\"input\":{"
        "\"name\":\"Support Smartphone %s\","
        "\"content\":\"Numero inventaire: %s\\n"
        "Modele: %s\\n"
        "Marque: %s\\n"
        "Android: %s (SDK %s)\\n"
        "Numero de serie: %s\\n"
        "Batterie: %s%%\""
        "}"
        "}'",
        GLPI_URL,
        GLPI_APP_TOKEN,
        session_token,
        info.model,
        info.inventory_number,
        info.model,
        info.brand,
        info.android_version,
        info.sdk_version,
        info.serial,
        info.battery_level
    );

    print_info("Creation ticket GLPI...");
    system(cmd);

    print_success("Ticket cree !");
}

/* ================= MENU ================= */

void display_menu() {
    printf("\n=== ABN SMARTPHONE ===\n");
    printf("1. Reset via ADB (Recovery)\n");
    printf("2. Reset via Fastboot\n");
    printf("3. Creer Ticket GLPI\n");
    printf("0. Quitter\n");
    printf("Choix: ");
}

int main() {

    int choice;

    while (1) {
        display_menu();

        if (scanf("%d", &choice) != 1) {
            while (getchar() != '\n');
            continue;
        }
        while (getchar() != '\n');

        switch(choice) {
            case 1:
                factory_reset_adb();
                break;
            case 2:
                factory_reset_fastboot();
                break;
            case 3:
                create_glpi_ticket();
                break;
            case 0:
                return 0;
            default:
                print_error("Choix invalide");
        }
    }
}

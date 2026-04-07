#include <stdio.h>

typedef struct {
    float health;
    float max_health;
    float x;
    float y;
    float speed;
} Player;

void calculate_player_health(Player *p, float damage) {
    p->health -= damage;
    if (p->health < 0) {
        p->health = 0;
    }
    printf("C Player took %.2f damage. Health: %.2f\n", damage, p->health);
}

void move_player(Player *p, float dx, float dy) {
    p->x += dx * p->speed;
    p->y += dy * p->speed;
    printf("C Player moved to (%.2f, %.2f)\n", p->x, p->y);
}

int main() {
    Player player = {100.0f, 100.0f, 0.0f, 0.0f, 5.0f};
    calculate_player_health(&player, 10.0f);
    move_player(&player, 1.0f, 0.0f);
    return 0;
}

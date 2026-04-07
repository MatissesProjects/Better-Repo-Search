#include <iostream>
#include <string>

class Player {
public:
    float health;
    float max_health;
    float x;
    float y;
    float speed;

    Player() : health(100.0f), max_health(100.0f), x(0.0f), y(0.0f), speed(5.0f) {}

    void calculate_player_health(float damage) {
        health -= damage;
        if (health < 0) health = 0;
        std::cout << "C++ Player took " << damage << " damage. Health: " << health << std::endl;
    }

    void move(float dx, float dy) {
        x += dx * speed;
        y += dy * speed;
        std::cout << "C++ Player moved to (" << x << ", " << y << ")" << std::endl;
    }
};

int main() {
    Player player;
    player.calculate_player_health(25.0f);
    player.move(1.0f, 1.0f);
    return 0;
}

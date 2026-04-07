struct Player {
    health: f32,
    max_health: f32,
    x: f32,
    y: f32,
    speed: f32,
}

impl Player {
    fn calculate_player_health(&mut self, damage: f32) {
        self.health -= damage;
        if self.health < 0.0 {
            self.health = 0.0;
        }
        println!("Rust Player took {} damage. Health: {}", damage, self.health);
    }

    fn move_player(&mut self, dx: f32, dy: f32) {
        self.x += dx * self.speed;
        self.y += dy * self.speed;
        println!("Rust Player moved to ({}, {})", self.x, self.y);
    }
}

fn main() {
    let mut player = Player {
        health: 100.0,
        max_health: 100.0,
        x: 0.0,
        y: 0.0,
        speed: 5.0,
    };
    player.calculate_player_health(15.0);
    player.move_player(1.0, 1.0);
}

package main

import "fmt"

type Player struct {
	Health    float64
	MaxHealth float64
	X         float64
	Y         float64
	Speed     float64
}

func (p *Player) calculate_player_health(damage float64) {
	p.Health -= damage
	if p.Health < 0 {
		p.Health = 0
	}
	fmt.Printf("Go Player took %v damage. Health: %v\n", damage, p.Health)
}

func (p *Player) move(dx, dy float64) {
	p.X += dx * p.Speed
	p.Y += dy * p.Speed
	fmt.Printf("Go Player moved to (%v, %v)\n", p.X, p.Y)
}

func main() {
	player := Player{Health: 100, MaxHealth: 100, Speed: 5}
	player.calculate_player_health(20)
	player.move(1, 0)
}

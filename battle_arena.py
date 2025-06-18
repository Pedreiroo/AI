import pygame
import random
from dataclasses import dataclass

WIDTH, HEIGHT = 800, 600
AGENT_RADIUS = 10
BULLET_RADIUS = 3
MAX_BOUNCES = 5
AGENT_SPEED = 2
BULLET_SPEED = 5

@dataclass
class Agent:
    x: float
    y: float
    color: pygame.Color

    def move(self):
        dx = random.uniform(-1, 1) * AGENT_SPEED
        dy = random.uniform(-1, 1) * AGENT_SPEED
        self.x = max(AGENT_RADIUS, min(WIDTH - AGENT_RADIUS, self.x + dx))
        self.y = max(AGENT_RADIUS, min(HEIGHT - AGENT_RADIUS, self.y + dy))

    def shoot(self, target):
        tx, ty = target.x - self.x, target.y - self.y
        dist = max((tx ** 2 + ty ** 2) ** 0.5, 1e-5)
        vx, vy = BULLET_SPEED * tx / dist, BULLET_SPEED * ty / dist
        return Bullet(self.x, self.y, vx, vy, self.color)

@dataclass
class Bullet:
    x: float
    y: float
    vx: float
    vy: float
    color: pygame.Color
    bounces: int = 0

    def update(self):
        self.x += self.vx
        self.y += self.vy

        if self.x <= BULLET_RADIUS or self.x >= WIDTH - BULLET_RADIUS:
            self.vx *= -1
            self.bounces += 1
        if self.y <= BULLET_RADIUS or self.y >= HEIGHT - BULLET_RADIUS:
            self.vy *= -1
            self.bounces += 1

    def is_alive(self):
        return self.bounces <= MAX_BOUNCES

def create_agents(num, color):
    agents = []
    for _ in range(num):
        x = random.uniform(AGENT_RADIUS, WIDTH - AGENT_RADIUS)
        y = random.uniform(AGENT_RADIUS, HEIGHT - AGENT_RADIUS)
        agents.append(Agent(x, y, color))
    return agents

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    red_agents = create_agents(5, pygame.Color('red'))
    blue_agents = create_agents(5, pygame.Color('blue'))
    bullets = []

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # agents take random actions
        for agents, enemies in ((red_agents, blue_agents), (blue_agents, red_agents)):
            for agent in agents:
                agent.move()
                if enemies:
                    target = random.choice(enemies)
                    if random.random() < 0.02:  # low prob to shoot
                        bullets.append(agent.shoot(target))

        # update bullets
        new_bullets = []
        for bullet in bullets:
            bullet.update()
            if bullet.is_alive():
                new_bullets.append(bullet)
        bullets = new_bullets

        # check collisions
        def handle_hits(shooters, targets):
            nonlocal bullets
            alive_targets = []
            for target in targets:
                hit = False
                for bullet in bullets:
                    if bullet.color == target.color:
                        continue
                    dist_sq = (bullet.x - target.x) ** 2 + (bullet.y - target.y) ** 2
                    if dist_sq <= (AGENT_RADIUS + BULLET_RADIUS) ** 2:
                        hit = True
                        break
                if not hit:
                    alive_targets.append(target)
            return alive_targets

        red_agents = handle_hits(blue_agents, red_agents)
        blue_agents = handle_hits(red_agents, blue_agents)

        # draw
        screen.fill((30, 30, 30))
        for agent in red_agents:
            pygame.draw.circle(screen, agent.color, (int(agent.x), int(agent.y)), AGENT_RADIUS)
        for agent in blue_agents:
            pygame.draw.circle(screen, agent.color, (int(agent.x), int(agent.y)), AGENT_RADIUS)
        for bullet in bullets:
            pygame.draw.circle(screen, bullet.color, (int(bullet.x), int(bullet.y)), BULLET_RADIUS)

        pygame.display.flip()
        clock.tick(60)

        if not red_agents or not blue_agents:
            running = False

    pygame.quit()

if __name__ == '__main__':
    main()

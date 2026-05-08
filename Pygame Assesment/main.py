import pygame
import sys
import subprocess

pygame.init()

WIDTH, HEIGHT = 320, 256

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED)

clock = pygame.time.Clock()


class world():

    def __init__(self):

        while True:

            screen.fill("white")

            font = pygame.font.SysFont("arial", 12)

            text1 = font.render(
                "what game do you want to play",
                True,
                "black"
            )

            text2 = font.render(
                "press 1 for space invaders",
                True,
                "black"
            )

            text3 = font.render(
                "press 2 for sonic",
                True,
                "black"
            )

            screen.blit(text1, (0, 0))
            screen.blit(text2, (0, 20))
            screen.blit(text3, (0, 40))

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_1:

                        pygame.quit()

                        subprocess.run(
                            ["python", "spaceinvadersmain.py"]
                        )

                        sys.exit()

                    if event.key == pygame.K_2:

                        pygame.quit()

                        subprocess.run(
                            ["python", "sonic.py"]
                        )

                        sys.exit()

            pygame.display.flip()
            clock.tick(60)


world()

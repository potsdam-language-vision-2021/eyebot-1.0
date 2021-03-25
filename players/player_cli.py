import click
import socketio


@click.command()
@click.option("--host", default="localhost")
@click.option("--port", default="5555", type=int)
@click.option('--game-role', type=click.Choice(['Director', 'Avatar'], case_sensitive=False), required=True)
def connect_and_play(host, port, game_role):
    sio = socketio.Client()

    @sio.event
    def message(data):
        print(data)

    custom_headers = {"X-Role": game_role, "X-Game-Mode": "demo"}
    sio.connect(f'http://{host}:{port}', headers=custom_headers)

    enter_message = None

    print("Hint: Type 'exit' to leave the game at any time.")
    while enter_message != "exit":
        enter_message = input()
        print(f"You: {enter_message}")
        sio.send(enter_message)

    sio.disconnect()


if __name__ == '__main__':
    connect_and_play()
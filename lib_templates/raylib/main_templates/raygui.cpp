#include <raylib.h>

#define RAYGUI_IMPLEMENTATION
#include <raygui.h>

int main() {
    const int screenWidth = 800;
    const int screenHeight = 450;

    InitWindow(screenWidth, screenHeight, "Raylib + Raygui - Simple Button");
    SetTargetFPS(60);

    bool buttonClicked = false;

    while (!WindowShouldClose()) {
        BeginDrawing();
        ClearBackground(RAYWHITE);

        if (GuiButton((Rectangle){ 350, 200, 100, 30 }, "Click Me")) {
            buttonClicked = true;
        }

        if (buttonClicked) {
            DrawText("Button was clicked!", 320, 250, 20, DARKGRAY);
        }

        EndDrawing();
    }

    CloseWindow();
    return 0;
}
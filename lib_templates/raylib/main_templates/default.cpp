#include <raylib.h>

int main() {
    // Initialize window
    const int screenWidth = 800;
    const int screenHeight = 450;
    InitWindow(screenWidth, screenHeight, "Raylib C++ - Hello Window");

    SetTargetFPS(60); // Set desired framerate

    while (!WindowShouldClose()) // Main game loop
    {
        BeginDrawing();
        ClearBackground(RAYWHITE);
        DrawText("Hello, Raylib!", 190, 200, 20, LIGHTGRAY);
        EndDrawing();
    }

    CloseWindow(); // Clean up
    return 0;
}
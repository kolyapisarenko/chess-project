#Chess Project X
Chess Project X is a custom chess engine and gaming platform developed in Python using the Pygame library. The project combines classic board game mechanics with modern machine learning methods.

Main concept
The project is divided into two strategic phases:

Phase 1: Logic & UI Core
Development of a proprietary chess engine from scratch (without third-party libraries for logic).
Implementation of a complete set of rules: castling, en passant, pawn promotion.
Advanced UI: pre-moves, visual analysis (arrows), move highlighting.

Phase 2: Self-Learning AI
Implementation of artificial intelligence.
Learning mechanics: AI analyzes each game played, adapting its strategy and position evaluation.

Game modes
PvP (Local): A game for two players on one computer.
PvE (Adaptive AI): Confrontation with a neural network that gets stronger with each game.

Current status (Sprint 1)
Currently implemented:
Centralized project configuration system.
Rendering of a chessboard with adaptive size.
Matrix model of the game state (GameState).
Automatic loading and centering of graphic assets for pieces.

Assets
The visual components of this project utilize JohnPablok's Improved Cburnett Chess Set.
Source: OpenGameArt.org
Author: JohnPablok

Key Features used in this project:
Proportional Scaling: We utilize the 1x/2x PNG sets where pieces have natural height variations (e.g., pawns are shorter than rooks) for a more realistic board feel.
HD Quality: High-definition pieces with consistent line widths and improved silhouettes (specifically the modified Knight and King).
Custom Squares: Using the provided brown/gray wood-style dark and light squares.

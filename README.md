# Multiplayer Game Prototype  
*A Python, Pygame & Sockets Experimental Project*

---

## 🚀 Overview

This repository presents an **experimental prototype** for a 2D multiplayer game
, built with Python, [Pygame](https://www.pygame.org/), and sockets.  
The main objective is to illustrate the fundamentals of real-time multiplayer
 game programming using a simple client-server architecture.

> **Disclaimer:**  
> This is **not** a full-featured or production-ready game.  
> It is a minimal, educational project designed for learning, prototyping, and
 experimentation.

---

## ✨ Features

- **Simple Pygame interface:** Move your player using arrow keys in a shared
 space.
- **Multiple players:** Join from different machines and see each other's
 positions live.
- **Basic synchronization:** Handles player join, leave, and movement updates
 over the network.
- **Modular design:** Clean codebase, easily extensible for further features or
 your own ideas.

---

## 🛠 Requirements

- Python 3.8+
- `pygame`
- `attrs`

Install dependencies with:

``bash``

```
pip install -r requirements.txt

```

---

## 🚦 Getting Started

### 1. Start the Server

Run the server to listen for incoming connections:

``bash``

```
python server.py

```
### 2. Start the Game Client

On the same or another machine, run:

``bash``

```
python game.py
```
> **Note:**  
> You can change the server address and port in `server.py` and `networking.py`
 as needed.

---

## 📁 Project Structure

- **server.py**    – Multiplayer server logic and player synchronization  
- **networking.py** – Client-side networking (connect, send, receive)  
- **player.py**    – Player class and attributes  
- **game.py**     – Main game loop, input, and rendering  
- **assets/**     – (Optional) images, sounds, or other resources
- **requirements.txt** – List of required Python packages

---

## ⚠️ Important Notes

- **Prototype only:** This is a learning and demonstration project, not a
 complete game.
- **No advanced features:** No chat, collision, scoring, or AI.
- **Minimal error handling:** Some edge cases may not be managed.
- **Open for extension:** Use as a foundation for your own multiplayer game
 ideas!

---

## 📜 License

Open source ― for educational and experimental purposes.

---

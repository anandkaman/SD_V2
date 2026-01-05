========================================
   SaleDeed Processor - Quick Guide
========================================

FIRST TIME SETUP (Only once):
------------------------------
1. Double-click SETUP.bat
2. Wait 5-10 minutes for installation
3. Done! Now you can use START.bat

Note: Installs packages globally (no venv needed)


HOW TO START:
-------------
1. Double-click START.bat
2. Wait 10-15 seconds
3. Desktop application opens automatically


HOW TO STOP:
-------------
1. Click X on the desktop app (will ask for confirmation)
   OR
2. Double-click STOP.bat (manual stop)


WHAT YOU'LL SEE:
----------------
- Background processes start (minimized)
- A desktop application window opens
  (Not a browser - it's a desktop app!)
- No terminal windows visible on screen


TROUBLESHOOTING:
----------------
Problem: "No module named uvicorn"
Solution: Run SETUP.bat to install dependencies

Problem: "node_modules not found"
Solution: Run SETUP.bat to install dependencies

Problem: Port already in use
Solution: Run STOP.bat first, then START.bat

Problem: Python or Node not found
Solution: Install Python 3.8+ and Node.js 16+


PORTS USED:
-----------
Backend:  8000
Frontend: 4000 (Electron desktop app)


========================================
That's it! Simple and easy.
========================================

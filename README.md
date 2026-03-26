# Study-Monitoring-System
The Study Monitoring System is a productivity tool developed as a final project for ENGI 1020. 
Study Monitoring System

The Study Monitoring System is a productivity tool developed as a final project for ENGI 1020. The system uses an Arduino Uno board, an LCD display, a distance sensor, and a sound sensor to monitor a user’s attention during study sessions. The goal of the system is to help users track how effectively they stay focused while studying or reading.

The program operates in two different modes: Study Mode and Reading Mode. Study Mode uses stricter thresholds for environmental noise and user presence, encouraging a quieter and more focused environment. Reading Mode allows slightly more background noise while still monitoring the user's attention. The distance sensor detects whether the user is present at their desk, while the sound sensor monitors surrounding noise levels. If the user moves too far away or the environment becomes too noisy, the system detects this as a distraction.

During each session, the LCD screen displays the amount of focused time and distracted time in real time, allowing the user to monitor their progress. If the system detects prolonged distraction, it alerts the user with a notification until they acknowledge it. At the end of a session, the program calculates a focus efficiency percentage, giving feedback on how productive the session was.

The system also records session data, including study time and distracted time, and saves it to a CSV file. This data can later be visualized using graphs generated with Matplotlib, allowing users to compare study and distraction times across sessions and over multiple days.

Overall, the Study Monitoring System combines hardware sensors and Python-based data analysis to create a practical tool that helps users improve their concentration and better understand their study habits.

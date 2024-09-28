import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
import os
import base64

# Vector class to represent an oscillating vector along the x-axis
class Vector:
    def __init__(self, amplitude, frequency, color, point_shape='o', point_size=10, line_style='-', dotted=False):
        """
        Initialize a Vector with its properties.

        Parameters:
        - amplitude (float): Amplitude of the oscillation (i.e., maximum x displacement).
        - frequency (float): Frequency of the sine wave oscillation (in Hz).
        - color (str): Color of the vector.
        - point_shape (str): Shape of the point (e.g., 'o' for circle, '^' for arrowhead).
        - point_size (int): Size of the point.
        - line_style (str): Style of the line ('-' for solid, '--' for dashed).
        - dotted (bool): Whether the line should be dotted or solid.
        """
        self.amplitude = amplitude
        self.frequency = frequency
        self.color = color
        self.point_shape = point_shape
        self.point_size = point_size
        self.line_style = line_style
        self.dotted = dotted

    def create_animation(self, duration=None, filename="oscillating_vector.mp4"):
        """
        Creates an animated oscillating vector using Matplotlib's FuncAnimation and saves it as an MP4.

        Parameters:
        - duration (float): Duration of the animation in seconds.
        - filename (str): The name of the MP4 file to save.

        Returns:
        - The file path of the saved MP4 video.
        """
        if duration is None:
            # Ensure the duration is set to one period of oscillation (1/frequency)
            duration = 1 / self.frequency  # Time for one full oscillation

        total_frames = int(duration * 60)  # 60 frames per second for smooth animation
        time = np.linspace(0, duration, total_frames)  # Generate time steps for the animation

        # Increase the DPI for higher resolution and anti-aliasing
        fig, ax = plt.subplots(figsize=(6, 2), dpi=200)
        ax.set_xlim(-self.amplitude - 1, self.amplitude + 1)
        ax.set_ylim(-1, 1)  # Keep it along the x-axis, so we can limit the y-axis range
        ax.set_aspect('auto')
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        ax.axhline(0, color='black', linewidth=0.5)
        ax.axvline(0, color='black', linewidth=0.5)

        # Define the line style, either dotted or solid
        line_style = '--' if self.dotted else self.line_style

        # Only plot the point moving along the x-axis based on the sine function
        vector_line, = ax.plot([], [], marker=self.point_shape, markersize=self.point_size, color=self.color, linestyle=line_style)

        def init():
            vector_line.set_data([], [])
            return vector_line,

        def update(frame):
            # Oscillate along the x-axis with a sine wave
            x = self.amplitude * np.sin(2 * np.pi * self.frequency * time[frame])
            y = 0  # Keep it fixed on the x-axis
            vector_line.set_data([0, x], [0, y])
            return vector_line,

        # Create the animation
        ani = FuncAnimation(fig, update, frames=total_frames, init_func=init, blit=True)

        # Save the animation to a local file using ffmpeg
        file_path = os.path.join(os.getcwd(), filename)
        ani.save(file_path, writer="ffmpeg", fps=60)

        return file_path

# Function to display video in loop using HTML
def display_video_in_loop(video_path):
    video_html = f"""
    <video width="100%" height="auto" controls autoplay loop>
        <source src="data:video/mp4;base64,{video_path}" type="video/mp4">
        Your browser does not support the video tag.
    </video>
    """
    st.markdown(video_html, unsafe_allow_html=True)

# Streamlit App Title
st.title("Interactive Oscillating Vector Animation")

# Sidebar for interactive controls
st.sidebar.header("Oscillation Configuration")

# Sidebar Inputs for the Vector
amplitude = st.sidebar.slider(
    "Amplitude (Max X Displacement)",
    min_value=0.1,
    max_value=5.0,
    value=2.0,
    step=0.1
)
frequency = st.sidebar.slider(
    "Frequency (Hz)",
    min_value=0.1,
    max_value=5.0,
    value=1.0,
    step=0.1
)
vector_color = st.sidebar.color_picker("Vector Color", value="#1f77b4")
vector_shape = st.sidebar.selectbox("Point Shape", options=['o', '^', 's', 'D', 'X'])
vector_size = st.sidebar.slider("Point Size", min_value=5, max_value=20, value=10, step=1)
vector_dotted = st.sidebar.checkbox("Dotted Line", value=False)

# Create the vector instance
vector = Vector(amplitude, frequency, vector_color, point_shape=vector_shape, point_size=vector_size, dotted=vector_dotted)

# The duration is calculated based on one full period of the sine wave (1 / frequency)
duration = 1 / frequency

# Display the oscillating vector animation as an MP4
if st.sidebar.button("Start Animation"):
    # Create animation for the vector
    video_file_path = vector.create_animation(duration=duration, filename="oscillating_vector.mp4")

    # Read video as bytes and encode it in base64
    with open(video_file_path, "rb") as video_file:
        video_bytes = video_file.read()
    encoded_video = base64.b64encode(video_bytes).decode('utf-8')

    # Display the video in loop
    st.markdown("### Oscillating Vector Animation")
    display_video_in_loop(encoded_video)

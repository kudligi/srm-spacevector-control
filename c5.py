import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
import os
import base64

# Function to create a text input with validation
def input_with_validation(label, value, step, min_value=None, max_value=None):
    input_val = st.sidebar.text_input(label, value=str(value), key=f"{label}_input")
    
    try:
        input_val = float(input_val)
        if min_value is not None and input_val < min_value:
            st.sidebar.warning(f"{label} cannot be less than {min_value}")
            input_val = min_value
        if max_value is not None and input_val > max_value:
            st.sidebar.warning(f"{label} cannot be greater than {max_value}")
            input_val = max_value
    except ValueError:
        st.sidebar.error(f"Invalid input for {label}. Using default value.")
        input_val = value  # Reset if invalid input
    
    return input_val

# Vector class to represent an oscillating vector along the x-axis or at a given angle
class Vector:
    def __init__(self, amplitude, frequency, angle=0, phase_shift=0, color='blue', point_shape='o', point_size=10, line_style='-', dotted=False):
        """
        Initialize a Vector with its properties.

        Parameters:
        - amplitude (float): Amplitude of the oscillation (i.e., maximum displacement).
        - frequency (float): Frequency of the sine wave oscillation (in Hz).
        - angle (float): Angle of the second vector in degrees relative to the x-axis.
        - phase_shift (float): Phase shift in degrees.
        - color (str): Color of the vector.
        - point_shape (str): Shape of the point (e.g., 'o' for circle, '^' for arrowhead).
        - point_size (int): Size of the point.
        - line_style (str): Style of the line ('-' for solid, '--' for dashed).
        - dotted (bool): Whether the line should be dotted or solid.
        """
        self.amplitude = amplitude
        self.frequency = frequency
        self.angle = np.radians(angle)  # Convert angle to radians
        self.phase_shift = np.radians(phase_shift)  # Convert phase shift to radians
        self.color = color
        self.point_shape = point_shape
        self.point_size = point_size
        self.line_style = line_style
        self.dotted = dotted

    def create_animation(self, other_vector, duration=None, filename="oscillating_vectors.mp4"):
        """
        Creates an animated oscillating vector with another vector using Matplotlib's FuncAnimation and saves it as an MP4.

        Parameters:
        - other_vector (Vector): The other vector to animate together.
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
        fig, ax = plt.subplots(figsize=(6, 6), dpi=200)
        ax.set_xlim(-self.amplitude - 1, self.amplitude + 1)
        ax.set_ylim(-self.amplitude - 1, self.amplitude + 1)
        ax.set_aspect('equal')
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        ax.axhline(0, color='black', linewidth=0.5)
        ax.axvline(0, color='black', linewidth=0.5)

        # Define the line style, either dotted or solid
        line_style_self = '--' if self.dotted else self.line_style
        line_style_other = '--' if other_vector.dotted else other_vector.line_style

        # Create two vectors: one on the x-axis and the other at a given angle
        vector_self, = ax.plot([], [], marker=self.point_shape, markersize=self.point_size, color=self.color, linestyle=line_style_self)
        vector_other, = ax.plot([], [], marker=other_vector.point_shape, markersize=other_vector.point_size, color=other_vector.color, linestyle=line_style_other)

        # Resultant vector (sum of the two)
        resultant_vector, = ax.plot([], [], marker='o', markersize=self.point_size + 2, color='green', linestyle='-', label='Resultant')

        def init():
            vector_self.set_data([], [])
            vector_other.set_data([], [])
            resultant_vector.set_data([], [])
            return vector_self, vector_other, resultant_vector

        def update(frame):
            # Calculate the oscillation for the first vector (x-axis)
            x_self = self.amplitude * np.sin(2 * np.pi * self.frequency * time[frame])
            y_self = 0

            # Calculate the oscillation for the second vector (at the given angle, with phase shift)
            x_other = other_vector.amplitude * np.cos(other_vector.angle) * np.sin(2 * np.pi * other_vector.frequency * time[frame] + other_vector.phase_shift)
            y_other = other_vector.amplitude * np.sin(other_vector.angle) * np.sin(2 * np.pi * other_vector.frequency * time[frame] + other_vector.phase_shift)

            # Resultant vector is the sum of the two components
            x_res = x_self + x_other
            y_res = y_self + y_other

            vector_self.set_data([0, x_self], [0, y_self])
            vector_other.set_data([0, x_other], [0, y_other])
            resultant_vector.set_data([0, x_res], [0, y_res])

            return vector_self, vector_other, resultant_vector

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
st.title("Interactive Oscillating Vectors with Resultant Vector Animation")

# Sidebar for shared controls for both vectors
st.sidebar.header("Shared Oscillation Configuration")

# Amplitude and Frequency configuration common to both vectors with input validation
amplitude = input_with_validation("Amplitude (Max Displacement for Both Vectors)", value=2.0, step=0.1, min_value=0.1, max_value=5.0)
frequency = input_with_validation("Frequency (Hz)", value=0.1, step=0.01, min_value=0.01, max_value=1.0)

# Color selection for both vectors on the same row
col1, col2 = st.sidebar.columns(2)

with col1:
    vector1_color = st.color_picker("Vector 1 Color", value="#1f77b4")
with col2:
    vector2_color = st.color_picker("Vector 2 Color", value="#ff7f0e")

# Additional configurations for points
vector_shape = st.sidebar.selectbox("Point Shape (Applies to Both Vectors)", options=['o', '^', 's', 'D', 'X'])
vector_size = input_with_validation("Point Size (Applies to Both Vectors)", value=10, step=1, min_value=5, max_value=20)
vector_dotted = st.sidebar.checkbox("Dotted Line for Both Vectors", value=False)

# Angle input for the second vector with input validation
angle_vector2 = input_with_validation("Angle of Vector 2 (Degrees)", value=45, step=1, min_value=0, max_value=360)

# Phase shift input for the second vector with input validation
phase_shift_vector2 = input_with_validation("Phase Shift of Vector 2 (Degrees)", value=90, step=1, min_value=0, max_value=360)

# Create instances for both vectors
vector1 = Vector(amplitude, frequency, angle=0, color=vector1_color, point_shape=vector_shape, point_size=vector_size, dotted=vector_dotted)
vector2 = Vector(amplitude, frequency, angle=angle_vector2, phase_shift=phase_shift_vector2, color=vector2_color, point_shape=vector_shape, point_size=vector_size, dotted=vector_dotted)

# The duration is calculated based on one full period of the sine wave (1 / frequency)
duration = 1 / frequency

# Display the oscillating vectors animation as an MP4
if st.sidebar.button("Start Animation"):
    # Create animation for the two vectors with the resultant vector
    video_file_path = vector1.create_animation(vector2, duration=duration, filename="oscillating_vectors.mp4")

    # Read video as bytes and encode it in base64
    with open(video_file_path, "rb") as video_file:
        video_bytes = video_file.read()
    encoded_video = base64.b64encode(video_bytes).decode('utf-8')

    # Display the video in loop
    st.markdown("### Oscillating Vectors with Resultant Vector Animation")
    display_video_in_loop(encoded_video)

import streamlit as st

# --- App Configuration ---
st.set_page_config(layout="wide")

# --- Helper Functions ---

def get_tissue_responses(exercise_type, intensity, reps, volume_duration, frequency, effort):
    """
    Calculates the likely net effect on Muscle, Tendon, and Bone based on inputs.
    Returns a dictionary with effects and explanations for each tissue.
    Effects: "▲ Increase", "▬ Maintain", "▼ Decrease", "⚠️ Potential Risk"
    """
    muscle_effect = "▬ Maintain"
    tendon_effect = "▬ Maintain"
    bone_effect = "▬ Maintain"
    muscle_exp = ""
    tendon_exp = ""
    bone_exp = ""

    is_resistance = "Resistance Training" in exercise_type
    is_weightbearing = "Standing" in exercise_type or "Running" in exercise_type or "Jumping" in exercise_type or "Walking" in exercise_type
    is_high_impact = "Jumping" in exercise_type
    is_moderate_impact = "Running" in exercise_type
    is_low_impact = "Walking" in exercise_type
    is_sedentary = "Sedentary" in exercise_type

    # --- Sedentary / Immobilized ---
    if is_sedentary:
        muscle_effect = "▼ Decrease"
        tendon_effect = "▼ Decrease"
        bone_effect = "▼ Decrease"
        muscle_exp = "Disuse leads to muscle atrophy, especially Type II fibers."
        tendon_exp = "Lack of mechanical load reduces collagen synthesis and strength."
        bone_exp = "Lack of dynamic loading leads to bone loss."
        return {"Muscle": (muscle_effect, muscle_exp), "Tendon": (tendon_effect, tendon_exp), "Bone": (bone_effect, bone_exp)}

    # --- General Frequency Check ---
    if frequency == "Infrequent (<1x / week)":
         # Infrequent activity is unlikely to drive significant positive adaptation and may lean towards maintenance or decrease depending on baseline
         muscle_exp += " Infrequent training limits adaptation stimulus. "
         tendon_exp += " Insufficient loading frequency for significant adaptation. "
         bone_exp += " Insufficient loading frequency for significant adaptation. "
         # Keep default as Maintain unless other factors push it down

    # --- Intensity Aliases for easier logic ---
    intensity_map = {
        "Very Low (<30% 1RM / RPE < 4)": 1,
        "Low (30-50% 1RM / RPE 4-6)": 2,
        "Moderate (50-80% 1RM / RPE 6-8)": 3,
        "High (80-95% 1RM / RPE 8-9)": 4,
        "Very High / Maximal (>95% 1RM / RPE 9.5-10)": 5
    }
    intensity_level = intensity_map.get(intensity, 0)

    # --- Volume Aliases ---
    volume_map = {
        "Very Low (<10 min / < 3 sets)": 1,
        "Low (10-20 min / 3-6 sets)": 2,
        "Moderate (20-45 min / 6-12 sets)": 3,
        "High (45-75 min / 12-20 sets)": 4,
        "Very High (>75 min / >20 sets)": 5
    }
    volume_level = volume_map.get(volume_duration, 0)

    # --- Frequency Aliases ---
    freq_map = {
        "Infrequent (<1x / week)": 1,
        "Low (1-2x / week)": 2,
        "Moderate (3-4x / week)": 3,
        "High (5-6x / week)": 4,
        "Very High (7+x / week)": 5
    }
    freq_level = freq_map.get(frequency, 0)

    # --- Effort Aliases ---
    effort_map = {
         "Low Effort (Far from failure)": 1,
         "Moderate Effort (Reps in reserve)": 2,
         "High Effort (1-2 reps shy)": 3,
         "To Failure": 4
    }
    effort_level = effort_map.get(effort, 0) if is_resistance else 0 # Effort only relevant for RT

    # --- Reps Aliases ---
    reps_map = {
        "Low (1-5 reps)": 1,
        "Moderate (6-12 reps)": 2,
        "High (13-20 reps)": 3,
        "Very High (20+ reps)": 4
    }
    reps_level = reps_map.get(reps, 0) if is_resistance else 0 # Reps only relevant for RT

    # --- Muscle Logic ---
    if is_resistance:
        muscle_effect = "▬ Maintain" # Default for resistance
        muscle_exp = "Resistance training stimulates muscle. "
        # Conditions for Increase
        if effort_level >= 3 and freq_level >= 2 and volume_level >= 2 and intensity_level >= 2:
             muscle_effect = "▲ Increase"
             if intensity_level >= 4 and reps_level <= 1 and effort_level >= 3:
                 muscle_exp += "High load, high effort promotes maximal strength gains. "
             elif intensity_level >= 2 and effort_level >= 4: # Training to failure
                 muscle_exp += "Training to failure, even with lighter loads, promotes hypertrophy/strength. "
             elif intensity_level >= 3 and reps_level == 2 and effort_level >= 3:
                 muscle_exp += "Moderate load/reps with high effort promotes hypertrophy/strength. "
             else:
                  muscle_exp += "Sufficient intensity, volume, frequency and effort drive adaptation. "
        elif freq_level <= 1 or volume_level <= 1 or effort_level <= 1:
            muscle_effect = "▬ Maintain" # May even decrease if truly minimal
            muscle_exp += "Low volume, frequency, or effort may only maintain current levels. "

        if volume_level >= 5 and freq_level >= 5 and intensity_level >=4:
             muscle_effect = "⚠️ Potential Risk"
             muscle_exp += "Very high intensity, volume & frequency increase overtraining risk. "

    elif is_high_impact or is_moderate_impact or is_low_impact:
        muscle_effect = "▬ Maintain"
        muscle_exp = "Activity engages muscles, helping maintain function. "
        if volume_level >= 3 and freq_level >= 3:
             muscle_exp += "Consistent activity helps maintain muscle mass involved. "
        if volume_level >=4 and freq_level >=4:
             muscle_effect = "▲ Increase" # Primarily endurance/specific hypertrophy
             muscle_exp += "High volume/frequency can increase endurance & potentially size of involved muscles. "
    else: # Non-weightbearing Cardio
        muscle_effect = "▬ Maintain"
        muscle_exp = "Cardio engages some muscles, helping maintain them. "
        if volume_level <= 1 and freq_level <= 1:
            muscle_effect = "▼ Decrease" # Minimal stimulus
            muscle_exp += "Very low volume/frequency may not be enough stimulus. "

    # --- Tendon Logic ---
    tendon_effect = "▬ Maintain" # Default if not sedentary
    tendon_exp = "Tendons require mechanical load. "
    if is_resistance or is_high_impact or is_moderate_impact:
         tendon_exp += "Exercise provides mechanical loading. "
         # Conditions for Increase
         if intensity_level >= 3 and freq_level >= 2 and volume_level >= 2: # Need sufficient load/volume/freq
              tendon_effect = "▲ Increase"
              if is_high_impact:
                   tendon_exp += "High impact loading provides strong stimulus for adaptation. "
              elif intensity_level >= 4:
                   tendon_exp += "High intensity resistance training increases stiffness/CSA. "
              elif is_moderate_impact and volume_level >= 3:
                   tendon_exp += "Consistent moderate impact (e.g., running) increases stiffness/CSA. "
              else:
                   tendon_exp += "Sufficient load, volume, and frequency drive adaptation. "

         # Conditions for Risk
         if (is_high_impact or intensity_level >= 4) and (volume_level >= 5 or freq_level >= 5):
             tendon_effect = "⚠️ Potential Risk"
             tendon_exp += "Very high volume/frequency of high load/impact increases overload/tendinopathy risk. "
         elif volume_level <= 1 or freq_level <= 1:
             tendon_effect = "▬ Maintain"
             tendon_exp += "Low volume or frequency limits adaptation stimulus. "

    elif is_low_impact: # Walking
        tendon_exp += "Low impact provides some loading. "
        if freq_level >= 3:
            tendon_effect = "▬ Maintain"
            tendon_exp += "Regular low impact loading helps maintain tendon properties. "
        else:
            tendon_effect = "▬ Maintain" # Unlikely to decrease unless already compromised
            tendon_exp += "Infrequent low impact provides minimal stimulus. "
    else: # Non-WB Cardio
        tendon_effect = "▼ Decrease" # Or Maintain if some minimal loading occurs
        tendon_exp = "Non-weightbearing exercise provides minimal tensile load to many tendons. "


    # --- Bone Logic ---
    bone_effect = "▬ Maintain" # Default if not sedentary
    bone_exp = "Bone requires dynamic, weightbearing load. "
    if is_weightbearing:
        bone_exp += "Weightbearing exercise provides loading stimulus. "
        # Conditions for Increase
        if (is_high_impact and freq_level >= 3) or \
           (is_resistance and intensity_level >= 3 and freq_level >= 3 and volume_level >= 2) or \
           (is_moderate_impact and freq_level >= 3 and volume_level >= 3):
            bone_effect = "▲ Increase"
            if is_high_impact:
                bone_exp += "High impact (high strain rate) is highly osteogenic. "
            elif is_resistance and intensity_level >= 3:
                bone_exp += "Moderate-to-high load resistance training stimulates bone formation. "
            elif is_moderate_impact:
                 bone_exp += "Consistent moderate impact (running) stimulates bone formation. "
            else:
                 bone_exp += "Sufficient dynamic, weightbearing load exceeding habitual levels drives adaptation. "

        elif is_low_impact and freq_level >= 3: # Walking
            bone_effect = "▬ Maintain"
            bone_exp += "Regular low-impact weightbearing helps maintain bone density. "
        elif freq_level <= 2 or volume_level <= 1 :
             bone_effect = "▬ Maintain" # Minimal stimulus likely only maintains
             bone_exp += "Low frequency or volume provides minimal osteogenic stimulus. "

        # Conditions for Risk (Mainly for high impact or pre-existing conditions)
        if is_high_impact and (volume_level >= 5 or freq_level >= 5):
            # Note: Risk is higher with poor technique or underlying issues, hard to model simply
            # bone_effect = "⚠️ Potential Risk" # Stress fracture risk
            bone_exp += "Very high volume/frequency of impact may increase stress fracture risk if not managed. "

    else: # Non-WB Resistance or Cardio
        bone_effect = "▼ Decrease" # Or Maintain if other WB activity exists
        bone_exp = "Non-weightbearing activity provides minimal osteogenic stimulus. May lead to loss if primary activity."

    # Final check for Infrequent - tends towards Maintain unless sedentary
    if freq_level == 1 and not is_sedentary:
        if muscle_effect == "▲ Increase": muscle_effect = "▬ Maintain"
        if tendon_effect == "▲ Increase": tendon_effect = "▬ Maintain"
        if bone_effect == "▲ Increase": bone_effect = "▬ Maintain"
        if muscle_effect == "▼ Decrease": muscle_effect = "▼ Decrease" # Stays decrease if already low
        if tendon_effect == "▼ Decrease": tendon_effect = "▼ Decrease"
        if bone_effect == "▼ Decrease": bone_effect = "▼ Decrease"


    return {"Muscle": (muscle_effect, muscle_exp), "Tendon": (tendon_effect, tendon_exp), "Bone": (bone_effect, bone_exp)}

# --- Streamlit App Layout ---

st.title("Tissue Adaptation Simulator")
st.markdown("""
This app simulates the likely **net effect** of different loading parameters on Muscle, Tendon, and Bone based on general physiological principles.
Adjust the parameters on the left to see how tissues might adapt.

**Disclaimer:** This is a simplified educational tool based on the provided text summaries. It does **not** provide medical or personalized training advice. Individual responses vary significantly. Consult qualified healthcare or fitness professionals for guidance. Progression and recovery are also critical factors not fully modelled here.
""")
st.divider()

# --- Input Parameters ---
st.sidebar.header("Loading Parameters")

exercise_type = st.sidebar.selectbox(
    "Exercise Type",
    [
        "Resistance Training - Standing (Weightbearing)",
        "Resistance Training - Seated/Supine (Non-Weightbearing)",
        "Running / Moderate Impact Cardio",
        "Jumping / High Impact Plyometrics",
        "Walking / Low Impact Weightbearing",
        "Cycling / Swimming (Non-Weightbearing Cardio)",
        "Sedentary / Immobilized",
    ]
)

intensity = st.sidebar.select_slider(
    "Intensity / Load",
    options=[
        "Very Low (<30% 1RM / RPE < 4)",
        "Low (30-50% 1RM / RPE 4-6)",
        "Moderate (50-80% 1RM / RPE 6-8)",
        "High (80-95% 1RM / RPE 8-9)",
        "Very High / Maximal (>95% 1RM / RPE 9.5-10)",
    ],
    value="Moderate (50-80% 1RM / RPE 6-8)" # Default value
)

# Conditional Inputs for Resistance Training
reps = "N/A"
effort = "N/A"
if "Resistance Training" in exercise_type:
    reps = st.sidebar.select_slider(
        "Volume - Reps per Set",
        options=["Low (1-5 reps)", "Moderate (6-12 reps)", "High (13-20 reps)", "Very High (20+ reps)"],
        value="Moderate (6-12 reps)"
    )
    effort = st.sidebar.select_slider(
        "Effort Level (RPE proximity)",
        options=["Low Effort (Far from failure)", "Moderate Effort (Reps in reserve)", "High Effort (1-2 reps shy)", "To Failure"],
        value="High Effort (1-2 reps shy)"
    )
else:
     st.sidebar.markdown("_(Reps/Effort specific to Resistance Training)_")


volume_duration = st.sidebar.select_slider(
    "Volume - Duration / Sets",
     options=[
        "Very Low (<10 min / < 3 sets)",
        "Low (10-20 min / 3-6 sets)",
        "Moderate (20-45 min / 6-12 sets)",
        "High (45-75 min / 12-20 sets)",
        "Very High (>75 min / >20 sets)",
     ],
     value="Moderate (20-45 min / 6-12 sets)"
)

frequency = st.sidebar.select_slider(
    "Frequency",
    options=[
        "Infrequent (<1x / week)",
        "Low (1-2x / week)",
        "Moderate (3-4x / week)",
        "High (5-6x / week)",
        "Very High (7+x / week)",
    ],
    value="Moderate (3-4x / week)"
)

# --- Calculate and Display Results ---

results = get_tissue_responses(exercise_type, intensity, reps, volume_duration, frequency, effort)

col1, col2, col3 = st.columns(3)

with col1:
    st.header("Muscle 💪")
    effect, explanation = results["Muscle"]
    if effect == "▲ Increase":
        st.subheader(":arrow_up: Increase")
    elif effect == "▬ Maintain":
        st.subheader(":heavy_minus_sign: Maintain")
    elif effect == "▼ Decrease":
        st.subheader(":arrow_down: Decrease")
    elif effect == "⚠️ Potential Risk":
        st.subheader(":warning: Potential Risk")
    st.info(explanation)


with col2:
    st.header("Tendon 🔗")
    effect, explanation = results["Tendon"]
    if effect == "▲ Increase":
        st.subheader(":arrow_up: Increase")
    elif effect == "▬ Maintain":
        st.subheader(":heavy_minus_sign: Maintain")
    elif effect == "▼ Decrease":
        st.subheader(":arrow_down: Decrease")
    elif effect == "⚠️ Potential Risk":
        st.subheader(":warning: Potential Risk")
    st.info(explanation)

with col3:
    st.header("Bone 🦴")
    effect, explanation = results["Bone"]
    if effect == "▲ Increase":
        st.subheader(":arrow_up: Increase")
    elif effect == "▬ Maintain":
        st.subheader(":heavy_minus_sign: Maintain")
    elif effect == "▼ Decrease":
        st.subheader(":arrow_down: Decrease")
    elif effect == "⚠️ Potential Risk":
        st.subheader(":warning: Potential Risk") # Less common directly from overload, more stress injury
    st.info(explanation)

st.divider()
st.markdown("_Remember: This simulation simplifies complex biological processes. Consult professionals for specific guidance._")
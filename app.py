import streamlit as st
import random
from streamlit_autorefresh import st_autorefresh

# --- Auto refresh every 500ms ---
st_autorefresh(interval=500, key="refresh")

# Hide the header, "Manage App" button, and "Made with Streamlit" footer
st.markdown(
    """
    <style>
    /* Hide the hamburger menu */
    #MainMenu {visibility: hidden;}
    
    /* Hide the footer */
    footer {visibility: hidden;}
    
    /* Hide the header */
    header {visibility: hidden;}

    /* Hide the "Deploy" button (useful for local testing) */
    .stDeployButton {display: none;}

    /* Target the "Manage App" button in the Community Cloud */
    .embeddedAppMetaInfoBar_container__DxxL1 {visibility: hidden;}
    </style>
""",
    unsafe_allow_html=True,
)

st.set_page_config(
    page_title="Xharis•DBD&D Character Sheet", page_icon="⚔️", layout="wide"
)


# --- Shared global state (persistent across sessions) ---
@st.cache_resource
def get_global_state():
    return {
        "roll_counter": 0,
        "latest_roll": "No rolls yet.",
        "meta": {
            "Size": "",
            "Build": "",
            "Level": "",
        },
        "stats": {
            "Might": 0,
            "Precision": 0,
            "Agility": 0,
            "Endurance": 0,
            "Immunity": 0,
            "Intellect": 0,
            "Focus": 0,
            "Insight": 0,
            "Influence": 0,
            "Power": 0,
            "Command": 0,
            "Talent": 0,
            "Talent Description": "",
            "Vulnerability": "",
            "Resistance": "",
            "Feature": "",
        },
    }


state = get_global_state()


# --- Dice helpers ---
def roll_dice(num_dice: int):
    rolls = [random.randint(1, 6) for _ in range(num_dice)]
    total = sum(rolls)
    return total


def interpret_roll(num_dice: int, total: int) -> str:
    if num_dice == 2:
        if total < 6:
            return "Failure | Regular Save | no-and"
        if total == 6:
            return "Success | Disadvantage on Save | yes-but"
        if total == 7:
            return "Critical Success | No Save | yes-and"
        if total == 8:
            return "Success | Disadvantage on Save | yes-but"
        if total > 8:
            return "Failure | Regular Save | no-but"
    if num_dice == 4:
        if total < 12:
            return "Failure | Regular Save | no-and"
        if total in (12, 13):
            return "Success | Disadvantage on Save | yes-but"
        if total == 14:
            return "Critical Success | No Save | yes-and"
        if total in (15, 16):
            return "Success | Disadvantage on Save | yes-but"
        if total > 16:
            return "Failure | Regular Save | no-but"
    if num_dice == 6:
        if total < 18:
            return "Failure | Regular Save | no-and"
        if 18 <= total <= 20:
            return "Success | Disadvantage on Save | yes-but"
        if total == 21:
            return "Critical Success | No Save | yes-and"
        if 22 <= total <= 24:
            return "Success | Disadvantage on Save | yes-but"
        if total > 24:
            return "Failure | Regular Save | no-but"
    return "unknown"


# --- UI ---
st.markdown(
    """
    <h2 style='text-align: center; margin-top: -105px; font-family: "Gill Sans", sans-serif;'>DBD&D Character Sheet</h2>
    """,
    unsafe_allow_html=True,
)

# --- Character metadata fields ---
st.subheader("Character Name")

meta_cols = st.columns(3)
with meta_cols[0]:
    state["meta"]["Size"] = st.text_input(
        "Size", value=state["meta"]["Size"], key="char_size"
    )
with meta_cols[1]:
    state["meta"]["Build"] = st.text_input(
        "Build", value=state["meta"]["Build"], key="char_build"
    )
with meta_cols[2]:
    state["meta"]["Level"] = st.text_input(
        "Level", value=state["meta"]["Level"], key="char_level"
    )

# --- Calculate total trait points ---
numeric_stats = {
    k: v for k, v in state["stats"].items() if isinstance(v, int) and k != "Talent"
}
total_points = sum(numeric_stats.values())
st.markdown(f"**Total Trait Points:** {total_points} / 20")

st.divider()

# --- Stats grid ---
stat_names = list(state["stats"].keys())
cols = st.columns(4)

for i, stat in enumerate(stat_names):
    col = cols[i % 4]
    with col:
        if stat in ["Talent Description", "Vulnerability", "Resistance", "Feature"]:
            state["stats"][stat] = st.text_input(
                stat, value=state["stats"][stat], key=f"{stat}_text"
            )
        else:
            # Button = label + roller (top)
            b1, b2, b3 = st.columns([2, 1, 1])
            val = state["stats"][stat]
            disabled = val == 0 or val == 4
            with b1:
                if st.button(
                    stat,
                    key=f"roll_{stat}",
                    disabled=disabled,
                    use_container_width=True,
                ):
                    num_dice = val * 2
                    total = roll_dice(num_dice)
                    outcome = interpret_roll(num_dice, total)
                    state["roll_counter"] += 1
                    state["latest_roll"] = (
                        f"Roll #{state['roll_counter']} | {stat} | {num_dice}d6 = {total} → {outcome}"
                    )

            with b2:
                if st.button(
                    "ADV",
                    key=f"roll_{stat}_adv",
                    disabled=(val + 1) >= 4,
                    use_container_width=True,
                ):
                    num_dice = (val + 1) * 2
                    total = roll_dice(num_dice)
                    outcome = interpret_roll(num_dice, total)
                    state["roll_counter"] += 1
                    state["latest_roll"] = (
                        f"Roll #{state['roll_counter']} | {stat} | {num_dice}d6 = {total} → {outcome}"
                    )
            with b3:
                if st.button(
                    "DIS",
                    key=f"roll_{stat}_dis",
                    disabled=(val - 1) <= 0,
                    use_container_width=True,
                ):
                    num_dice = (val - 1) * 2
                    total = roll_dice(num_dice)
                    outcome = interpret_roll(num_dice, total)
                    state["roll_counter"] += 1
                    state["latest_roll"] = (
                        f"Roll #{state['roll_counter']} | {stat} | {num_dice}d6 = {total} → {outcome}"
                    )

            # Editable stat points (below the button)
            new_val = st.number_input(
                f"{stat}_val",
                value=state["stats"][stat],
                key=f"{stat}_val",
                step=1,
                min_value=0,
                max_value=4,
                label_visibility="collapsed",
            )
            state["stats"][stat] = new_val

# --- Latest roll field ---
st.text_area("Latest Roll", value=state["latest_roll"], height=50, disabled=True)

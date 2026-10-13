import math
import streamlit as st
import streamlit.components.v1 as components

# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="High-Performance Scientific Calculator",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ============================================================
# CUSTOM CSS & HYBRID KEYBOARD BRIDGE
# ============================================================
st.markdown(
    """
    <style>
        .stApp {
            background: linear-gradient(135deg, #090d16, #111827);
        }
        .main .block-container {
            max-width: 520px;
            padding-top: 1.5rem;
            padding-bottom: 2rem;
        }
        .calculator-title {
            text-align: center;
            font-size: 2.2rem;
            font-weight: 700;
            color: #f8fafc;
            margin-bottom: 0.1rem;
        }
        .calculator-subtitle {
            text-align: center;
            color: #64748b;
            font-size: 0.9rem;
            margin-bottom: 1.5rem;
        }
        .display-box {
            background: #030712;
            border: 1px solid #1e293b;
            border-radius: 16px;
            padding: 18px 22px;
            margin-bottom: 16px;
            box-shadow: inset 0 2px 6px rgba(0, 0, 0, 0.6);
        }
        .display-expression {
            color: #64748b;
            font-size: 0.95rem;
            min-height: 22px;
            text-align: right;
            word-wrap: break-word;
            font-family: monospace;
        }
        .display-result {
            color: #38bdf8;
            font-size: 2.3rem;
            font-weight: 600;
            text-align: right;
            word-wrap: break-word;
            font-family: monospace;
        }
        .section-title {
            color: #94a3b8;
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin: 12px 0 6px 0;
        }
        div.stButton > button {
            width: 100%;
            height: 48px;
            border-radius: 10px;
            border: 1px solid #1e293b;
            background: #1e293b;
            color: #f8fafc;
            font-size: 1rem;
            font-weight: 600;
            transition: transform 0.08s ease, background 0.1s ease;
        }
        div.stButton > button:hover {
            background: #334155;
            border-color: #475569;
        }
        div.stButton > button:active {
            transform: scale(0.96);
        }
        .history-box {
            max-height: 140px;
            overflow-y: auto;
            background: #0b0f19;
            border: 1px solid #1e293b;
            border-radius: 10px;
            padding: 10px;
            margin-top: 15px;
        }
        .history-item {
            color: #94a3b8;
            font-size: 0.85rem;
            font-family: monospace;
            padding: 3px 0;
            border-bottom: 1px solid #111827;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================
if "expression" not in st.session_state:
    st.session_state.expression = ""
if "result" not in st.session_state:
    st.session_state.result = "0"
if "history" not in st.session_state:
    st.session_state.history = []
if "angle_mode" not in st.session_state:
    st.session_state.angle_mode = "DEG"
if "action_trigger" not in st.session_state:
    st.session_state.action_trigger = None

# ============================================================
# EVALUATION & CALCULATION ENGINE
# ============================================================
def format_result(value):
    if isinstance(value, float):
        if math.isfinite(value):
            if value.is_integer():
                return str(int(value))
            return f"{value:.12g}"
    return str(value)

def factorial(value):
    if value < 0 or not float(value).is_integer():
        raise ValueError("Factorial requires a non-negative integer.")
    return math.factorial(int(value))

def safe_eval(expression):
    expression = expression.replace("×", "*").replace("÷", "/").replace("^", "**").replace("π", "pi")
    
    if st.session_state.angle_mode == "DEG":
        sin, cos, tan = lambda x: math.sin(math.radians(x)), lambda x: math.cos(math.radians(x)), lambda x: math.tan(math.radians(x))
        asin, acos, atan = lambda x: math.degrees(math.asin(x)), lambda x: math.degrees(math.acos(x)), lambda x: math.degrees(math.atan(x))
    else:
        sin, cos, tan, asin, acos, atan = math.sin, math.cos, math.tan, math.asin, math.acos, math.atan

    allowed_names = {
        "sin": sin, "cos": cos, "tan": tan, "asin": asin, "acos": acos, "atan": atan,
        "sinh": math.sinh, "cosh": math.cosh, "tanh": math.tanh,
        "log10": math.log10, "ln": math.log, "sqrt": math.sqrt,
        "factorial": factorial, "abs": abs, "exp": math.exp,
        "pi": math.pi, "e": math.e,
    }

    try:
        res = eval(expression, {"__builtins__": {}}, allowed_names)
        if isinstance(res, complex):
            raise ValueError("Complex results not supported.")
        if not math.isfinite(float(res)):
            raise ValueError("Result is not finite.")
        return format_result(res)
    except ZeroDivisionError:
        raise ValueError("Cannot divide by zero.")
    except ValueError as e:
        raise ValueError(str(e))
    except OverflowError:
        raise ValueError("Number too large.")
    except Exception:
        raise ValueError("Invalid expression.")

def perform_calculation():
    expr = st.session_state.expression.strip()
    if not expr:
        return
    try:
        res = safe_eval(expr)
        st.session_state.result = res
        st.session_state.history.insert(0, f"{expr} = {res}")
        st.session_state.history = st.session_state.history[:15]
        st.session_state.expression = res
    except ValueError as err:
        st.session_state.result = f"Error: {err}"

# Handle action requests triggered by UI buttons or keyboard mapper
action = st.session_state.pop("action_trigger", None)
if action:
    if action == "=":
        perform_calculation()
    elif action == "AC":
        st.session_state.expression = ""
        st.session_state.result = "0"
    elif action == "⌫":
        if st.session_state.expression:
            st.session_state.expression = st.session_state.expression[:-1]
    elif action.startswith("FUNC:"):
        fn = action.split(":")[1]
        expr = st.session_state.expression.strip() or "0"
        if fn in ["sqrt", "exp"]:
            map_name = {"sqrt": "sqrt", "exp": "exp"}[fn]
            st.session_state.expression = f"{map_name}({expr})"
        elif fn == "x²":
            st.session_state.expression = f"({expr})**2"
        elif fn == "xʸ":
            st.session_state.expression = f"({expr})**"
        elif fn == "x!":
            st.session_state.expression = f"factorial({expr})"
        elif fn == "+/-":
            st.session_state.expression = f"-({expr})"
        elif fn == "%":
            st.session_state.expression = f"({expr})/100"
        else:
            st.session_state.expression = f"{fn}({expr})"
    else:
        st.session_state.expression += action

# ============================================================
# UI HEADER & MODE TOGGLE
# ============================================================
st.markdown('<div class="calculator-title">TALHA |🧮 Scientific Calculator</div>', unsafe_allow_html=True)
st.markdown('<div class="calculator-subtitle">Optimized Speed • Keyboard & Mouse Ready</div>', unsafe_allow_html=True)

col_mode1, col_mode2 = st.columns([3, 1])
with col_mode1:
    st.markdown('<div class="section-title">Mode</div>', unsafe_allow_html=True)
with col_mode2:
    st.session_state.angle_mode = st.selectbox(
        "Mode", ["DEG", "RAD"],
        index=0 if st.session_state.angle_mode == "DEG" else 1,
        label_visibility="collapsed"
    )

# ============================================================
# DISPLAY SCREEN
# ============================================================
st.markdown(
    f"""
    <div class="display-box">
        <div class="display-expression">{st.session_state.expression if st.session_state.expression else '&nbsp;'}</div>
        <div class="display-result">{st.session_state.result}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# BUTTON LAYOUT & CALLBACK GENERATOR
# ============================================================
def make_callback(val):
    def cb():
        st.session_state.action_trigger = val
    return cb

# Scientific Grid
sci_rows = [
    ["sin", "cos", "tan", "asin", "acos", "atan"],
    ["sinh", "cosh", "tanh", "log10", "ln", "√"],
    ["x²", "xʸ", "x!", "abs", "eˣ", "π"],
    ["e", "(", ")", "⌫", "AC", "="]
]

st.markdown('<div class="section-title">Scientific</div>', unsafe_allow_html=True)
for row in sci_rows:
    cols = st.columns(len(row))
    for i, btn in enumerate(row):
        with cols[i]:
            val_to_pass = f"FUNC:{btn}" if btn in ["sin","cos","tan","asin","acos","atan","sinh","cosh","tanh","log10","ln","√","x²","xʸ","x!","abs","eˣ"] else btn
            st.button(btn, key=f"sci_{btn}_{i}", on_click=make_callback(val_to_pass), use_container_width=True)

# Basic Grid
basic_rows = [
    ["7", "8", "9", "÷"],
    ["4", "5", "6", "×"],
    ["1", "2", "3", "-"],
    ["0", ".", "%", "+"],
    ["+/-", "AC", "⌫", "="]
]

st.markdown('<div class="section-title">Basic</div>', unsafe_allow_html=True)
for r_idx, row in enumerate(basic_rows):
    cols = st.columns(4)
    for i, btn in enumerate(row):
        with cols[i]:
            val_to_pass = btn if btn not in ["+/-", "%"] else f"FUNC:{btn}"
            st.button(btn, key=f"bas_{r_idx}_{i}", on_click=make_callback(val_to_pass), use_container_width=True)

# ============================================================
# HISTORY PANEL
# ============================================================
st.markdown('<div class="section-title">History</div>', unsafe_allow_html=True)
if st.session_state.history:
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.history = []
        st.rerun()
    
    hist_html = "<div class='history-box'>"
    for item in st.session_state.history:
        hist_html += f"<div class='history-item'>{item}</div>"
    hist_html += "</div>"
    st.markdown(hist_html, unsafe_allow_html=True)
else:
    st.caption("No history yet.")

# ============================================================
# HIGH-PERFORMANCE PHYSICAL KEYBOARD LISTENER
# ============================================================
components.html("""
<script>
const doc = window.parent.document;
doc.addEventListener('keydown', function(e) {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    
    let key = e.key;
    let buttons = Array.from(doc.querySelectorAll('button'));
    let targetText = null;
    
    if ((key >= '0' && key <= '9') || key === '.' || key === '(' || key === ')' || key === '+' || key === '-') {
        targetText = key;
    } else if (key === '*') {
        targetText = '×';
    } else if (key === '/') {
        targetText = '÷';
    } else if (key === '%') {
        targetText = '%';
    } else if (key === 'Enter' || key === '=') {
        targetText = '=';
    } else if (key === 'Backspace') {
        targetText = '⌫';
    } else if (key === 'Escape') {
        targetText = 'AC';
    }
    
    if (targetText) {
        let btn = buttons.find(b => b.innerText.trim() === targetText);
        if (btn) {
            btn.click();
            e.preventDefault();
        }
    }
});
</script>
""", height=0, width=0)
import json
import copy

DEBUG = False

output = {
    "multipart": []
}

directions = ["north", "south", "east", "west"]
less_directions = ["north", "east"]


def get_rotation(direction):
    if direction == "north":
        return 180
    elif direction == "east":
        return 270
    elif direction == "south":
        return 0
    elif direction == "west":
        return 90
    return None


def get_opposite_facing(direction):
    if direction == "north":
        return "south"
    elif direction == "east":
        return "west"
    elif direction == "south":
        return "north"
    elif direction == "west":
        return "east"
    return None


def apply_condition(condition, f):
    if "AND" in condition:
        for c in condition["AND"]:
            apply_condition(c, f)
    elif "OR" in condition:
        for c in condition["OR"]:
            apply_condition(c, f)
    else:
        f(condition)


def add_diagonal_facing(state, facing):
    def apply_diagonal_facing(condition):
        if "slope" in condition:
            if condition["slope"] == "downward":
                condition["facing"] = facing
            else:
                condition["facing"] = get_opposite_facing(facing)

    apply_condition(state["when"], apply_diagonal_facing)


# Diagonal belts
diagonal_belt_states = [
    {
        "when": {"AND": [
            {"OR": [{"part": "middle"}, {"part": "pulley"}]},
            {"OR": [{"slope": "downward"}, {"slope": "upward"}]}
        ]},
        "apply": {"model": "create:block/belt/diagonal_middle"}
    },
    {
        "when": {"OR": [
            {"part": "end", "slope": "downward"},
            {"part": "start", "slope": "upward"}
        ]},
        "apply": {"model": "create:block/belt/diagonal_start"}
    },
    {
        "when": {"OR": [
            {"part": "start", "slope": "downward"},
            {"part": "end", "slope": "upward"}
        ]},
        "apply": {"model": "create:block/belt/diagonal_end"}
    }
]

for facing in directions:
    for state in diagonal_belt_states:
        state = copy.deepcopy(state)
        state["apply"]["y"] = get_rotation(facing)
        add_diagonal_facing(state, facing)
        output["multipart"].append(state)

# Horizontal/Vertical/Sideways belts
non_diagonal_belt_states = [
    [
        {"part": "start"},
        "create:block/belt/start"
    ],
    [
        {"OR": [{"part": "middle"}, {"part": "pulley"}]},
        "create:block/belt/middle"
    ],
    [
        {"part": "end"},
        "create:block/belt/end"
    ]
]

for facing in directions:
    for state in non_diagonal_belt_states:
        for suffix in ["", "_bottom"]:
            output["multipart"].append({
                "when": {
                    "AND": [
                        state[0],
                        {"facing": facing, "slope": "horizontal"}
                    ]
                },
                "apply": {
                    "model": state[1] + suffix,
                    "y": get_rotation(facing)
                }
            })

            model = state[1]
            if facing == "west" or facing == "north":
                if "start" in model:
                    model = "create:block/belt/end"
                elif "end" in model:
                    model = "create:block/belt/start"

            output["multipart"].append({
                "when": {
                    "AND": [
                        state[0],
                        {"facing": facing, "slope": "vertical"}
                    ]
                },
                "apply": {
                    "model": model + suffix,
                    "y": get_rotation(facing),
                    "x": 90
                }
            })

            path_parts = state[1].split("/")
            model = "/".join(["bluemap_create:block"] + path_parts[1:-1] + ["sideways_"+path_parts[-1]])

            output["multipart"].append({
                "when": {
                    "AND": [
                        state[0],
                        {"facing": facing, "slope": "sideways"}
                    ]
                },
                "apply": {
                    "model": model + suffix,
                    "y": get_rotation(facing)
                }
            })


# Pulley
for facing in less_directions:
    output["multipart"].append({
        "when": {
            "AND": [
                {"OR": [
                    {"part": "start"},
                    {"part": "pulley"},
                    {"part": "end"}
                ]},
                {"OR": [
                    {"facing": facing},
                    {"facing": get_opposite_facing(facing)},
                ]},
                {"OR": [
                    {"slope": "horizontal"},
                    {"slope": "upward"},
                    {"slope": "downward"},
                    {"slope": "vertical"}
                ]}
            ]
        },
        "apply": {
            "model": "create:block/belt_pulley",
            "y": get_rotation(facing) + 90,
            "x": 90
        }
    })

output["multipart"].append({
    "when": {
        "AND": [
            {"OR": [
                {"part": "start"},
                {"part": "pulley"},
                {"part": "end"}
            ]},
            {"slope": "sideways"}
        ]
    },
    "apply": {
        "model": "create:block/belt_pulley",
        "x": 0
    }
})

# Casing
# Diagonal casing
diagonal_casing_states = [
    {
        "when": {"AND": [
            {"part": "middle"},
            {"OR": [{"slope": "downward"}, {"slope": "upward"}]}
        ]},
        "apply": {"model": "create:block/belt_casing/diagonal_middle"}
    },
    {
        "when": {"AND": [
            {"part": "pulley"},
            {"OR": [{"slope": "downward"}, {"slope": "upward"}]}
        ]},
        "apply": {"model": "create:block/belt_casing/diagonal_pulley"}
    },
    {
        "when": {"AND": [
            {
                "OR": [
                    {"part": "end", "slope": "downward"},
                    {"part": "start", "slope": "upward"}
                ]
            }
        ]},
        "apply": {"model": "create:block/belt_casing/diagonal_start"}
    },
    {
        "when": {"AND": [
            {
                "OR": [
                    {"part": "start", "slope": "downward"},
                    {"part": "end", "slope": "upward"}
                ]
            }
        ]},
        "apply": {"model": "create:block/belt_casing/diagonal_end"}
    }
]

for facing in directions:
    for state in diagonal_casing_states:
        state = copy.deepcopy(state)
        state["apply"]["y"] = get_rotation(facing)
        state["when"]["AND"].append({"casing": "true"})
        add_diagonal_facing(state, facing)
        output["multipart"].append(state)

# Horizontal/Vertical/Sideways casing
non_diagonal_casing_states = [
    [
        {"part": "start"},
        "create:block/belt_casing/horizontal_start"
    ],
    [
        {"part": "middle"},
        "create:block/belt_casing/horizontal_middle"
    ],
    [
        {"part": "pulley"},
        "create:block/belt_casing/horizontal_pulley"
    ],
    [
        {"part": "end"},
        "create:block/belt_casing/horizontal_end"
    ]
]

for facing in directions:
    for state in non_diagonal_casing_states:
        output["multipart"].append({
            "when": {
                "AND": [
                    state[0],
                    {"facing": facing, "slope": "horizontal", "casing": "true"}
                ]
            },
            "apply": {
                "model": state[1],
                "y": get_rotation(facing)
            }
        })

        model = state[1].replace("horizontal", "sideways")
        if facing == "west" or facing == "north":
            if "start" in model:
                model = "bluemap_create:block/belt_casing/sideways_end"
            elif "end" in model:
                model = "bluemap_create:block/belt_casing/sideways_start"

        output["multipart"].append({
            "when": {
                "AND": [
                    state[0],
                    {"facing": facing, "slope": "vertical", "casing": "true"}
                ]
            },
            "apply": {
                "model": model,
                "x": 90,
                "y": (get_rotation(facing) + 90) % 360
            }
        })

        output["multipart"].append({
            "when": {
                "AND": [
                    state[0],
                    {"facing": facing, "slope": "sideways", "casing": "true"}
                ]
            },
            "apply": {
                "model": model,
                "y": get_rotation(facing)
            }
        })


with open("assets/create/blockstates/belt.json", "w") as file:
    if DEBUG:
        json.dump(output, file, indent=4)
    else:
        json.dump(output, file)

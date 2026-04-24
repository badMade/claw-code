import sys


def replace_in_file(filepath, search_str, replace_str):
    with open(filepath, "r") as f:
        content = f.read()

    if search_str in content:
        content = content.replace(search_str, replace_str)
        with open(filepath, "w") as f:
            f.write(content)
        print("Replacement successful.")
    else:
        print("Search string not found.")


search = """fn agent_detail(agent: &AgentSummary) -> String {
    let mut parts = vec![agent.name.as_str()];
    if let Some(description) = &agent.description {
        parts.push(description.as_str());
    }
    if let Some(model) = &agent.model {
        parts.push(model.as_str());
    }
    if let Some(reasoning) = &agent.reasoning_effort {
        parts.push(reasoning.as_str());
    }
    parts.join(" · ")
}"""

replace = """fn agent_detail(agent: &AgentSummary) -> String {
    let parts: Vec<&str> = [
        Some(agent.name.as_str()),
        agent.description.as_deref(),
        agent.model.as_deref(),
        agent.reasoning_effort.as_deref(),
    ]
    .into_iter()
    .flatten()
    .collect();
    parts.join(" · ")
}"""

replace_in_file("rust/crates/commands/src/lib.rs", search, replace)

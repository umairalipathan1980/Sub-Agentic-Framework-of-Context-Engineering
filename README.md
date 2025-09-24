# Claude Code's Sub-Agentic Framework for Context Engineering

A specialized, autonomous sub-agent framework for Claude Code that transforms software development workflows through intelligent task delegation and context-aware routing. This is the first version of the framework with limited number of sub-agents. It will remain under evolution by updates from contributors. 

## Overview

The Claude Sub-Agent Framework consists of 12 specialized sub-agents and 11 command triggers that work together to handle every aspect of software development, from project analysis to feature implementation to quality assurance. Each agent has distinct expertise, tools, and validation procedures, creating a true autonomous intelligence system rather than generic task handling.

## Key Features

- **Autonomous Specialization**: 12 sub-agents with distinct expertise and decision-making capabilities
- **Conditional Routing**: Commands intelligently choose between agents based on project context
- **Incremental Intelligence**: Preserves existing work and only updates what has actually changed
- **Validation Gates**: Phase-by-phase validation ensures working code at each milestone
- **Web-Aware**: Agents can search for and cite authoritative external documentation
- **Safety-Constrained**: Read-only operations with systematic token conservation
- **Highly Customizable**: Add agents, modify existing ones, or redefine commands for specific workflows

## Quick Start

### Installation

Run the setup script to create the complete framework structure:

```bash
bash setup_claude_multi_agents_script.sh
```

This creates:
```
.claude/
├── agents/          # 12 specialized sub-agents
├── commands/        # 11 command triggers
├── examples/        # Code patterns and reference implementations
├── PRPs/           # Product Requirements Prompts (generated)
├── CLAUDE.md       # Main project blueprint (13 sections)
└── INITIAL.md      # Feature request template (4 sections)
```

### Basic Usage

1. **Analyze your project**:
   ```bash
   /analyze
   ```

2. **Create a feature request**:
   ```bash
   /create-feature-request "Add user authentication system"
   ```

3. **Generate implementation blueprint**:
   ```bash
   /generate-prp INITIAL.md
   ```

4. **Execute the feature**:
   ```bash
   /execute-prp PRPs/user-authentication.md
   ```

5. **Document the completed feature**:
   ```bash
   /update-new-feature-doc "user authentication"
   ```

## Architecture

### Sub-Agent Categories

**Analysis & Discovery Agents**: These agents understand and analyze projects to establish context and create foundational documentation.
- `greenfield-initializer` - Bootstrap brand-new repositories
- `project-analyzer` - Comprehensive project understanding  
- `minor-analyzer` - Incremental change analysis

**Feature Development Agents**: These agents transform ideas into structured requirements and implement them through validated execution.
- `feature-requestor` - Convert ideas to structured requirements
- `prp-generator` - Create implementation blueprints
- `prp-executor` - Execute blueprints with validation

**Documentation Agents**: These agents maintain project documentation at both system-wide and directory levels based on completed work.
- `feature-documentor` - Document completed features
- `commit-documentor` - Document from git history
- `directory-documentor` - Maintain directory READMEs

**Quality & Review Agents**: These agents evaluate code changes and overall project health for security, performance, and maintainability.
- `change-reviewer` - Review recent code changes
- `project-reviewer` - Comprehensive project audits

**Summary & Overview Agent**: This agent provides concise, actionable project summaries for developers joining or reviewing the codebase.
- `project-summarizer` - Generate project summaries

### Command Reference

| Command | Triggered Agent(s) | Purpose |
|---------|-------------------|---------|
| `/bootstrap-initial` | `greenfield-initializer` | Bootstrap brand new repositories |
| `/analyze` | `minor-analyzer` OR `project-analyzer` | Smart conditional analysis |
| `/refresh` | `project-analyzer` | Force complete re-analysis |
| `/create-feature-request` | `feature-requestor` | Create INITIAL.md |
| `/generate-prp` | `prp-generator` | Create implementation blueprint |
| `/execute-prp` | `prp-executor` | Execute implementation |
| `/update-new-feature-doc` | `feature-documentor` | Document completed feature |
| `/update-new-feature-from-commits` | `commit-documentor` | Document from git history |
| `/summarize` | `project-summarizer` | Project summary |
| `/review` | `change-reviewer` OR `project-reviewer` | Conditional code review |
| `/create-directory-docs` | `directory-documentor` | Create subdirectory docs |

## Development Workflow

1. **Discovery**: `/analyze` or `/summarize` to understand current project state
2. **Planning**: `/create-feature-request` → `/generate-prp` for detailed blueprints  
3. **Implementation**: `/execute-prp` with phase-by-phase validation
4. **Documentation**: `/update-new-feature-doc` or `/update-new-feature-from-commits`
5. **Quality**: `/review current` or `/review complete`

## Core Templates

### CLAUDE.md Structure (13 sections)
1. Overview
2. Architecture and System Design
3. Tech Stack & Environment
4. Key Code and File Structure
5. Functional Requirements / Features
6. Non-Functional Requirements
7. Integration Points & Dependencies
8. Environment / Ops & Dev Workflow
9. Recent Changes / Changelog Highlights
10. Testing, Quality & Standards
11. Risks, Edge Cases, and Open Questions
12. Glossary & Conventions
13. References & External Resources

### INITIAL.md Structure (4 sections)
- **FEATURE**: Problem description, requirements, acceptance criteria
- **EXAMPLES**: Reference implementations and usage patterns
- **DOCUMENTATION**: Required updates and external links
- **OTHER CONSIDERATIONS**: Edge cases, security, performance notes

## Conditional Intelligence

The framework implements smart routing:
- `/analyze` chooses between `minor-analyzer` (incremental updates) and `project-analyzer` (complete analysis) based on existing CLAUDE.md content
- `/review` chooses between `change-reviewer` (recent changes) and `project-reviewer` (comprehensive audit) based on arguments

## Customization

### Adding New Agents
1. Create agent specification in `.claude/agents/your-agent.md`
2. Define tools, constraints, and operating procedures
3. Add corresponding command trigger in `.claude/commands/`

### Modifying Existing Agents
1. Edit agent files to change behavior, tools, or constraints
2. Update command triggers if routing logic changes
3. Modify templates (CLAUDE.md, INITIAL.md) if needed

### Custom Workflows
- Modify command routing logic for your team's needs
- Add new template sections for domain-specific requirements
- Integrate with existing CI/CD pipelines and tools

## Safety & Constraints

- All agents use read-only operations by default
- Bash commands limited to safe, non-destructive operations
- Systematic token conservation through targeted file discovery
- Validation gates prevent broken code from advancing
- External documentation verified through web search

## Requirements

- Claude Code environment
- Git repository (recommended)
- Write access to create `.claude/` directory structure

## Contributing

We welcome contributions to the Claude Sub-Agent Framework! This project benefits from diverse perspectives and use cases from the development community. Whether you want to add new specialized agents, improve existing ones, or enhance the command routing system, your contributions can help make this framework more powerful and useful for teams worldwide.

### Ways to Contribute

- **New Sub-Agents**: Create agents for specific domains like database management, API testing, or deployment workflows
- **Enhanced Commands**: Improve conditional routing logic or add new command patterns
- **Template Improvements**: Refine the CLAUDE.md or INITIAL.md templates based on real-world usage
- **Documentation**: Add examples, tutorials, or clarify existing documentation
- **Bug Fixes**: Report issues or submit fixes for agent behavior or command routing
- **Integration Guides**: Help integrate the framework with popular tools and platforms

### Getting Started

1. Fork the repository at [https://github.com/umairalipathan1980/Sub-Agentic-Framework-of-Context-Engineering](https://github.com/umairalipathan1980/Sub-Agentic-Framework-of-Context-Engineering)
2. Create your feature branch (`git checkout -b feature/your-enhancement`)
3. Follow the existing agent specification format in `.claude/agents/`
4. Add validation procedures and safety constraints
5. Update documentation and command mappings as needed
6. Test your changes with real projects to ensure they work as expected
7. Submit a pull request with a clear description of your changes

## License

MIT License - see LICENSE file for details.

## Support

For issues, feature requests, or questions about extending the framework, please open an issue on GitHub or consult the generated CLAUDE.md in your project for specific implementation details.
/**
 * Workshop agent commands
 *
 * Registers one /<name> command per agent in .pi/agents, e.g.
 *   /ui-renderer build the visual foundation of the game
 * and /agents, which picks an agent for the next message you type.
 *
 * The transcript shows exactly what the user typed. A hidden message tells the
 * model to hand the request to that agent through the subagent tool.
 */

import type { ExtensionAPI, ExtensionContext } from "@earendil-works/pi-coding-agent";
import { discoverAgents } from "../subagent/agents.ts";

const NEXT_AGENT_WIDGET = "workshop-next-agent";

function shortDescription(description: string): string {
	const text = description.replace(/\s+/g, " ").trim();
	const sentence = text.split(/(?<=\.)\s/)[0];
	return sentence.length > 70 ? `${sentence.slice(0, 69)}…` : sentence;
}

export default function (pi: ExtensionAPI) {
	const agents = discoverAgents(process.cwd(), "project").agents;
	let pending: { prompt: string; agent: string; task: string } | undefined;
	let nextAgent: string | undefined;

	const setNextAgent = (ctx: ExtensionContext, name: string | undefined) => {
		nextAgent = name;
		ctx.ui.setWidget(
			NEXT_AGENT_WIDGET,
			name
				? [
						ctx.ui.theme.fg("accent", `→ Your next message goes to ${name}`) +
							ctx.ui.theme.fg("dim", " (/agents to change)"),
					]
				: undefined,
		);
	};

	for (const agent of agents) {
		pi.registerCommand(agent.name, {
			description: agent.description.replace(/\s+/g, " ").trim(),
			handler: async (args, ctx) => {
				const task = args.trim();
				if (!task) {
					ctx.ui.notify(`Usage: /${agent.name} <what to build>`, "warning");
					return;
				}
				if (!ctx.isIdle()) {
					ctx.ui.notify("Agent is busy. Wait for it to finish, then try again.", "warning");
					return;
				}
				const prompt = `/${agent.name} ${task}`;
				pending = { prompt, agent: agent.name, task };
				pi.sendUserMessage(prompt);
			},
		});
	}

	pi.registerCommand("agents", {
		description: "Pick a workshop agent to handle your next message",
		handler: async (_args, ctx) => {
			const labels = agents.map((a) => `${a.name} — ${shortDescription(a.description)}`);
			const none = "none — send it to the main agent";
			const choice = await ctx.ui.select("Send your next message to which agent?", [...labels, none]);
			if (choice === undefined) return;
			setNextAgent(ctx, agents[labels.indexOf(choice)]?.name);
		},
	});

	// A plain message typed after /agents goes to the chosen agent, once.
	pi.on("input", async (event, ctx) => {
		if (!nextAgent || event.source !== "interactive" || event.streamingBehavior) return;
		const task = event.text.trim();
		if (!task || task.startsWith("/") || task.startsWith("!")) return;
		pending = { prompt: event.text, agent: nextAgent, task };
		setNextAgent(ctx, undefined);
	});

	pi.on("before_agent_start", async (event) => {
		if (event.messageType !== "user" || !pending || event.prompt.trim() !== pending.prompt.trim()) return;
		const { agent, task } = pending;
		pending = undefined;
		return {
			message: {
				customType: "workshop-agent-dispatch",
				display: false,
				content: [
					`The user addressed this request to the "${agent}" agent.`,
					`Call the subagent tool once with agent: "${agent}", agentScope: "project" and task: ${JSON.stringify(task)}.`,
					"Do not read or edit game.html yourself.",
					"When the subagent finishes, reply with one or two sentences on what it changed.",
				].join("\n"),
			},
		};
	});
}

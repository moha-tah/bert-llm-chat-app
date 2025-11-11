export interface DefaultPrompt {
  id: string;
  title: string;
  prompt: string;
  category?: string;
}

export const defaultPrompts: DefaultPrompt[] = [
  {
    id: "1",
    title: "Aircraft maintenance procedures",
    prompt: "What are the key maintenance procedures for aircraft ground support equipment?",
    category: "Maintenance",
  },
  {
    id: "2",
    title: "Safety protocols",
    prompt: "What safety protocols should be followed when operating Barfield test equipment?",
    category: "Safety",
  },
  {
    id: "3",
    title: "Troubleshooting guides",
    prompt: "How do I troubleshoot common issues with pressure testing equipment?",
    category: "Troubleshooting",
  },
  {
    id: "4",
    title: "Equipment specifications",
    prompt: "What are the technical specifications for Barfield portable test equipment?",
    category: "Technical",
  },
];

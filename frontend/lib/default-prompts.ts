export interface DefaultPrompt {
  id: string;
  title: string;
  prompt: string;
  category?: string;
}

export const defaultPrompts: DefaultPrompt[] = [
  {
    id: "1",
    title: "TT1200A Temperature Range",
    prompt: "What is the temperature range of the Barfield TT1200A?",
    category: "Equipment",
  },
  {
    id: "2",
    title: "Transformer BLEU Score",
    prompt: "What BLEU score did the Transformer achieve on WMT 2014?",
    category: "AI/ML",
  },
  {
    id: "3",
    title: "Air France Fleet Size",
    prompt: "How many aircraft does Air France have in its fleet?",
    category: "Aviation",
  },
  {
    id: "4",
    title: "First Airline Flight",
    prompt: "When was the first scheduled airline flight conducted?",
    category: "History",
  },
];

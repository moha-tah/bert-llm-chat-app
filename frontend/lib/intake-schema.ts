import { z } from "zod";

/**
 * Support Intake Schema
 *
 * This schema defines the structured data we extract from user conversations
 * in the support intake widget. The AI assistant is responsible for populating
 * these fields through a guided conversation.
 */
export const IntakeSchema = z.object({
  purpose: z
    .enum([
      "report_issue",
      "check_status",
      "quote_request",
      "technical_question",
      "other",
    ])
    .nullable(),
  reason: z.string().nullable(),
  defective_part: z.string().nullable(),
  part_reference: z.string().nullable(),
  urgency: z.enum(["low", "medium", "high"]).nullable(),
  contact: z
    .object({
      name: z.string().nullable(),
      email: z.string().email().nullable(),
      phone: z.string().nullable(),
    })
    .nullable(),
  additional_notes: z.string().nullable(),
  missing: z.array(z.string()).default([]),
  confidence: z.enum(["low", "medium", "high"]).nullable(),
  recommended_team: z
    .enum([
      "engine",
      "hydraulic",
      "avionics",
      "landing_gear",
      "cabin",
      "default",
    ])
    .nullable(),
});

export type Intake = z.infer<typeof IntakeSchema>;

/**
 * Recommended team mapping for display purposes
 */
export const TEAM_MAPPING: Record<string, string> = {
  engine: "Engine Maintenance",
  hydraulic: "Hydraulics Team",
  avionics: "Avionics Support",
  landing_gear: "Landing Gear Team",
  cabin: "Cabin Systems",
  default: "General Technical Support",
};

/**
 * Purpose mapping for display purposes
 */
export const PURPOSE_MAPPING: Record<string, string> = {
  report_issue: "Report an Issue",
  check_status: "Check Status",
  quote_request: "Quote Request",
  technical_question: "Technical Question",
  other: "Other",
};

"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  type Intake,
  TEAM_MAPPING,
  PURPOSE_MAPPING,
} from "@/lib/intake-schema";
import { CheckCircle2, AlertCircle, Info } from "lucide-react";
import { cn } from "@/lib/utils";

interface SummaryCardProps {
  data: Intake;
  onEdit?: () => void;
  onSubmit?: () => void;
}

/**
 * SummaryCard Component
 *
 * Displays the extracted intake data in a structured format
 * Shows recommended team, confidence level, and any missing fields
 */
export function SummaryCard({ data, onEdit, onSubmit }: SummaryCardProps) {
  const recommendedTeam =
    (data.recommended_team && TEAM_MAPPING[data.recommended_team]) ||
    "General Technical Support";
  const purpose =
    (data.purpose && PURPOSE_MAPPING[data.purpose]) || data.purpose;
  const hasMissingFields = data.missing && data.missing.length > 0;

  return (
    <Card className="w-full border-[--color-oxford-blue]">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-lg">
          <CheckCircle2 className="h-5 w-5 text-[--color-pigment-red]" />
          Intake Summary
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Main Information */}
        <div className="space-y-3">
          <SummaryField label="Purpose" value={purpose} />
          <SummaryField label="Reason" value={data.reason} />
          <SummaryField label="Defective Part" value={data.defective_part} />
          <SummaryField label="Part Reference" value={data.part_reference} />
          <SummaryField
            label="Urgency"
            value={data.urgency}
            badge
            badgeColor={getUrgencyColor(data.urgency)}
          />
          {data.additional_notes && (
            <SummaryField label="Notes" value={data.additional_notes} />
          )}
        </div>

        {/* Contact Information */}
        {data.contact && (
          <div className="border-t pt-3">
            <h4 className="text-sm font-semibold mb-2">Contact Information</h4>
            <div className="space-y-2">
              <SummaryField label="Name" value={data.contact.name} small />
              <SummaryField label="Email" value={data.contact.email} small />
              <SummaryField label="Phone" value={data.contact.phone} small />
            </div>
          </div>
        )}

        {/* Routing Information */}
        <div className="border-t pt-3">
          <h4 className="text-sm font-semibold mb-2">Routing Information</h4>
          <div className="space-y-2">
            <SummaryField
              label="Recommended Team"
              value={recommendedTeam}
              icon={<Info className="h-4 w-4" />}
            />
            <SummaryField
              label="Confidence"
              value={data.confidence}
              badge
              badgeColor={getConfidenceColor(data.confidence)}
            />
          </div>
        </div>

        {/* Missing Fields Warning */}
        {hasMissingFields && (
          <div className="border-t pt-3">
            <div className="flex items-start gap-2 p-3 bg-yellow-50 dark:bg-yellow-950/20 border border-yellow-200 dark:border-yellow-900 rounded-md">
              <AlertCircle className="h-5 w-5 text-yellow-600 dark:text-yellow-500 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm font-medium text-yellow-900 dark:text-yellow-100">
                  Some information is missing
                </p>
                <p className="text-xs text-yellow-700 dark:text-yellow-300 mt-1">
                  {data.missing.join(", ")}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-2 pt-2">
          {onEdit && (
            <Button variant="outline" onClick={onEdit} className="flex-1">
              Edit
            </Button>
          )}
          {onSubmit && (
            <Button onClick={onSubmit} className="flex-1">
              Submit Request
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

/**
 * Individual field display component
 */
function SummaryField({
  label,
  value,
  badge = false,
  badgeColor,
  small = false,
  icon,
}: {
  label: string;
  value: string | null | undefined;
  badge?: boolean;
  badgeColor?: string;
  small?: boolean;
  icon?: React.ReactNode;
}) {
  if (!value) {
    return (
      <div className={cn("flex items-center gap-2", small && "text-sm")}>
        <span className="text-muted-foreground">{label}:</span>
        <span className="text-muted-foreground italic">Not provided</span>
      </div>
    );
  }

  return (
    <div className={cn("flex items-center gap-2", small && "text-sm")}>
      {icon}
      <span className="text-muted-foreground">{label}:</span>
      {badge ? (
        <span
          className={cn(
            "px-2 py-0.5 rounded-full text-xs font-medium capitalize",
            badgeColor
          )}
        >
          {value}
        </span>
      ) : (
        <span className="font-medium">{value}</span>
      )}
    </div>
  );
}

/**
 * Returns Tailwind classes for urgency badge colors
 */
function getUrgencyColor(urgency: string | null | undefined): string {
  switch (urgency) {
    case "high":
      return "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-200";
    case "medium":
      return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-200";
    case "low":
      return "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-200";
    default:
      return "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200";
  }
}

/**
 * Returns Tailwind classes for confidence badge colors
 */
function getConfidenceColor(confidence: string | null | undefined): string {
  switch (confidence) {
    case "high":
      return "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-200";
    case "medium":
      return "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-200";
    case "low":
      return "bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-200";
    default:
      return "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200";
  }
}

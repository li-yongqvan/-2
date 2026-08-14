import { readFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const sampleDir = resolve(__dirname, '../../../../../../data/samples/cyber-game-m9');

function readJsonl(filename: string): any[] {
  const text = readFileSync(resolve(sampleDir, filename), 'utf-8');
  return text
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => JSON.parse(line));
}

function readJson(filename: string): any {
  const text = readFileSync(resolve(sampleDir, filename), 'utf-8');
  return JSON.parse(text);
}

export interface ExperienceUnit {
  unit_id: string;
  decision_id: string;
  session_fragment_ids: string[];
  git_evidence_ids: string[];
  tag_ids: string[];
  course_module_ids: string[];
  learning_path_ids: string[];
  entry_points: { type: string; label: string; tag_id: string }[];
  related_unit_ids: string[];
  review_status: string;
  reviewer_notes: string;
  created_at: string;
  updated_at: string;
}

export interface SessionFragment {
  fragment_id: string;
  session_id: string;
  source_session_file: string;
  anchor_message_uuid: string;
  start_message_uuid: string;
  end_message_uuid: string;
  message_uuids: string[];
  summary: string;
  participants: string[];
  includes_subagent: boolean;
  alignment_quality: string;
  notes?: string;
}

export interface GitHunkEvidence {
  evidence_id: string;
  commit_sha: string;
  parent_commit_sha: string;
  file_path: string;
  hunk_index: number;
  diff_command?: string;
  code_ref: string;
  hunk: {
    old_start: number;
    new_start: number;
    old_lines: number;
    new_lines: number;
    header: string;
    lines?: string;
  };
  notes?: string;
  alignment_quality: string;
}

export interface DecisionPoint {
  id: string;
  title: string;
  category: string;
  category_en: string;
  source: string;
  source_type: string;
  question: string;
  options: { label: string; consequence: string }[];
  selected_option: string;
  rationale: string;
  affected_files: string[];
  unresolved_tail: string;
  timestamp: string;
  related_commit: string;
  experience_unit_id: string;
}

export const experienceUnits: ExperienceUnit[] = readJsonl('experience-units-v0.2.jsonl');
export const sessionFragments: SessionFragment[] = readJsonl('session-fragments-v0.2.jsonl');
export const gitHunkEvidence: GitHunkEvidence[] = readJsonl('git-hunk-evidence-v0.2.jsonl');
export const decisionPoints: DecisionPoint[] = readJsonl('decision-points-v0.2.jsonl');
export const tags = readJson('tags-v0.2.json');
export const courseModules: {
  module_id: string;
  title: string;
  description: string;
  entry_type: string;
  unit_sequence: { unit_id: string; rationale: string }[];
}[] = readJson('course-modules-v0.2.json');

export const fragmentById = new Map(sessionFragments.map((f) => [f.fragment_id, f]));
export const hunkById = new Map(gitHunkEvidence.map((h) => [h.evidence_id, h]));
export const decisionById = new Map(decisionPoints.map((d) => [d.id, d]));
export const unitById = new Map(experienceUnits.map((u) => [u.unit_id, u]));
export const tagById = new Map(tags.tags.map((t: any) => [t.id, t]));
export const moduleById = new Map(courseModules.map((m) => [m.module_id, m]));

export function unitDecision(unit: ExperienceUnit): DecisionPoint | undefined {
  return decisionById.get(unit.decision_id);
}

export function unitFragments(unit: ExperienceUnit): SessionFragment[] {
  return unit.session_fragment_ids
    .map((id) => fragmentById.get(id))
    .filter(Boolean) as SessionFragment[];
}

export function unitHunks(unit: ExperienceUnit): GitHunkEvidence[] {
  return unit.git_evidence_ids
    .flatMap((id) => {
      // git_evidence_ids are like `git-{sha}-{file}`; hunk evidence ids are `git-hunk-{sha}-{file}-{index}`.
      const hunkPrefix = id.replace(/^git-/, 'git-hunk-');
      return gitHunkEvidence.filter((h) => h.evidence_id.startsWith(hunkPrefix));
    })
    .filter(Boolean);
}

export function tagLabel(tagId: string): string {
  const t = tagById.get(tagId);
  return t ? `${t.label_zh} (${t.label_en})` : tagId;
}

export function moduleTitle(moduleId: string): string {
  const m = moduleById.get(moduleId);
  return m ? m.title : moduleId;
}

export function methodTags(): { id: string; label_zh: string; label_en: string }[] {
  return tags.tags.filter((t: any) => t.axis_id === 'method');
}

export function phaseTags(): { id: string; label_zh: string; label_en: string }[] {
  return tags.tags.filter((t: any) => t.axis_id === 'project_phase');
}

export function unitsByMethodTag(): Map<string, ExperienceUnit[]> {
  const map = new Map<string, ExperienceUnit[]>();
  for (const unit of experienceUnits) {
    for (const ep of unit.entry_points.filter((e) => e.type === 'method')) {
      if (!map.has(ep.tag_id)) map.set(ep.tag_id, []);
      map.get(ep.tag_id)!.push(unit);
    }
  }
  return map;
}

export function unitsByModule(): Map<string, ExperienceUnit[]> {
  const map = new Map<string, ExperienceUnit[]>();
  for (const unit of experienceUnits) {
    for (const modId of unit.course_module_ids) {
      if (!map.has(modId)) map.set(modId, []);
      map.get(modId)!.push(unit);
    }
  }
  return map;
}

export function formatDate(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleString('zh-CN', { dateStyle: 'short', timeStyle: 'short' });
}

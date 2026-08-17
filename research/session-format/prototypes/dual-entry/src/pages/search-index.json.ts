import type { APIRoute } from 'astro';
import { experienceUnits, decisionPoints, tagById, unitFragments } from '../data/loader.ts';

/**
 * Build a static search index at /search-index.json.
 *
 * Phase 1 scope:
 * - Only units with review_status === 'approved' are indexed.
 * - Each capture/insight slice becomes its own searchable document so that
 *   results can be presented per-slice rather than per-unit.
 */

export interface SearchDoc {
  unit_id: string;
  slice_id: string;
  slice_type: 'unit' | 'decision' | 'fragment' | 'tag';
  title: string;
  summary: string;
  text: string;
  tags: string[];
  url: string;
}

function tagLabels(tagIds: string[]): string[] {
  return tagIds
    .map((id) => tagById.get(id))
    .filter(Boolean)
    .map((t: any) => `${t.label_zh} ${t.label_en}`);
}

function buildIndex(): SearchDoc[] {
  const docs: SearchDoc[] = [];
  const approvedUnits = experienceUnits.filter((u) => u.review_status === 'approved');

  for (const unit of approvedUnits) {
    const decision = decisionPoints.find((d) => d.id === unit.decision_id);
    const fragments = unitFragments(unit);
    const unitTags = tagLabels(unit.tag_ids);
    const baseText = [
      unit.unit_id,
      decision?.title ?? '',
      decision?.question ?? '',
      ...unitTags,
    ].join(' ');

    // Unit-level document.
    docs.push({
      unit_id: unit.unit_id,
      slice_id: unit.unit_id,
      slice_type: 'unit',
      title: decision?.title ?? unit.unit_id,
      summary: decision?.question ?? unit.reviewer_notes ?? '',
      text: baseText,
      tags: unitTags,
      url: `unit/${unit.unit_id}`,
    });

    // Decision slice.
    if (decision) {
      docs.push({
        unit_id: unit.unit_id,
        slice_id: decision.id,
        slice_type: 'decision',
        title: decision.title,
        summary: decision.question,
        text: [
          decision.title,
          decision.question,
          decision.rationale,
          ...decision.options.map((o) => `${o.label} ${o.consequence}`),
          ...decision.affected_files,
        ].join(' '),
        tags: unitTags,
        url: `unit/${unit.unit_id}#decision`,
      });
    }

    // Fragment / insight slices.
    for (const frag of fragments) {
      docs.push({
        unit_id: unit.unit_id,
        slice_id: frag.fragment_id,
        slice_type: 'fragment',
        title: decision?.title ?? unit.unit_id,
        summary: frag.summary,
        text: [frag.fragment_id, frag.summary, frag.participants.join(' ')].join(' '),
        tags: unitTags,
        url: `unit/${unit.unit_id}#fragment-${frag.fragment_id}`,
      });
    }
  }

  return docs;
}

export const GET: APIRoute = () => {
  const docs = buildIndex();
  return new Response(JSON.stringify(docs), {
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      'Cache-Control': 'public, max-age=3600',
    },
  });
};

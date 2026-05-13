const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

export type Project = {
  id: string;
  name: string;
  status: string;
  created_at: string;
  updated_at: string;
};

export type Asset = {
  id: string;
  project_id: string;
  type: string;
  filename: string;
  original_url: string;
  created_at: string;
};

export type EditPlan = {
  id: string;
  project_id: string;
  asset_id: string;
  target_platform: string;
  aspect_ratio: string;
  duration_seconds: number | null;
  plan: Record<string, any>;
  status: string;
  created_at: string;
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: init?.body instanceof FormData ? init.headers : { "Content-Type": "application/json", ...init?.headers },
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed: ${response.status}`);
  }
  return response.json();
}

export function createProject(name: string) {
  return request<Project>("/projects", {
    method: "POST",
    body: JSON.stringify({ name }),
  });
}

export function uploadAsset(projectId: string, file: File) {
  const formData = new FormData();
  formData.append("file", file);
  return request<Asset>(`/projects/${projectId}/assets`, {
    method: "POST",
    body: formData,
  });
}

export function generatePlans(input: {
  projectId: string;
  assetId: string;
  targetPlatform: string;
  aspectRatio: string;
  versionCount: number;
  userGoal?: string;
  creativeTone: string;
  aiProvider?: string;
}) {
  return request<EditPlan[]>(`/projects/${input.projectId}/generate`, {
    method: "POST",
    body: JSON.stringify({
      asset_id: input.assetId,
      target_platform: input.targetPlatform,
      aspect_ratio: input.aspectRatio,
      version_count: input.versionCount,
      user_goal: input.userGoal,
      creative_tone: input.creativeTone,
      ai_provider: input.aiProvider,
    }),
  });
}

export function updateEditPlan(
  editPlanId: string,
  payload: {
    title?: string;
    hook?: string;
    caption_lines?: string[];
    visual_style?: string;
    effect_style?: string;
    bgm_style?: string;
    bgm_volume?: number;
  },
) {
  return request<EditPlan>(`/edit-plans/${editPlanId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function rerenderEditPlan(editPlanId: string) {
  return request<EditPlan>(`/edit-plans/${editPlanId}/render`, {
    method: "POST",
    body: JSON.stringify({}),
  });
}

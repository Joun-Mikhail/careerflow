/** Shared API types mirroring the backend Pydantic schemas. */

export type ApplicationStatus =
  | 'wishlist'
  | 'applied'
  | 'assessment'
  | 'interview'
  | 'final_interview'
  | 'offer'
  | 'rejected'
  | 'accepted';

export type InterviewMode = 'phone' | 'video' | 'onsite';
export type InterviewResult = 'pending' | 'passed' | 'failed' | 'cancelled';
export type TaskPriority = 'low' | 'medium' | 'high';
export type AttachmentKind = 'resume' | 'cover_letter' | 'other';

export interface User {
  id: string;
  email: string;
  full_name: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Token {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface AuthResponse {
  user: User;
  token: Token;
}

export interface Company {
  id: string;
  name: string;
  website: string | null;
  industry: string | null;
  location: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface Application {
  id: string;
  company_id: string | null;
  role_title: string;
  status: ApplicationStatus;
  salary_min: number | null;
  salary_max: number | null;
  salary_currency: string | null;
  location: string | null;
  is_remote: boolean;
  application_url: string | null;
  source: string | null;
  applied_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface Interview {
  id: string;
  application_id: string;
  scheduled_at: string;
  round_type: string | null;
  interviewer: string | null;
  mode: InterviewMode;
  result: InterviewResult;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface Task {
  id: string;
  title: string;
  description: string | null;
  priority: TaskPriority;
  due_at: string | null;
  application_id: string | null;
  is_completed: boolean;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface Note {
  id: string;
  application_id: string;
  body: string;
  created_at: string;
  updated_at: string;
}

export interface Attachment {
  id: string;
  application_id: string;
  kind: AttachmentKind;
  original_filename: string;
  content_type: string;
  size_bytes: number;
}

export interface Page<T> {
  items: T[];
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}

export interface DashboardSummary {
  totals: {
    applications: number;
    interviews: number;
    offers: number;
    rejections: number;
    accepted: number;
    pending_tasks: number;
  };
  success_rate: number;
  upcoming_interviews: {
    id: string;
    application_id: string;
    role_title: string | null;
    scheduled_at: string;
    mode: InterviewMode;
    result: InterviewResult;
  }[];
  pending_tasks: {
    id: string;
    title: string;
    priority: TaskPriority;
    due_at: string | null;
  }[];
  recent_applications: Application[];
}

export interface MonthCount {
  month: string;
  count: number;
}
export interface StatusCount {
  status: string;
  count: number;
}
export interface IndustryCount {
  industry: string;
  count: number;
}
export interface ConversionRates {
  total_applications: number;
  interview_rate: number;
  offer_rate: number;
}

export interface ApiErrorBody {
  error: {
    code: string;
    message: string;
    details?: unknown;
  };
}

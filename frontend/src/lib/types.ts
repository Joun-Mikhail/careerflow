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
export type OfferDecision = 'pending' | 'negotiating' | 'accepted' | 'declined';

// --- Smart job-search: document vault ---
export type CvSource = 'uploaded' | 'ai_tailored';
export type SkillProficiency = 'beginner' | 'intermediate' | 'advanced' | 'expert';

export interface Cv {
  id: string;
  title: string;
  source: CvSource;
  is_default: boolean;
  original_filename: string | null;
  content_type: string | null;
  size_bytes: number | null;
  parent_cv_id: string | null;
  job_id: string | null;
  has_file: boolean;
  created_at: string;
  updated_at: string;
}

export interface Certificate {
  id: string;
  name: string;
  issuer: string | null;
  issued_on: string | null;
  credential_url: string | null;
  original_filename: string | null;
  content_type: string | null;
  size_bytes: number | null;
  has_file: boolean;
  created_at: string;
  updated_at: string;
}

export interface Skill {
  id: string;
  name: string;
  category: string | null;
  proficiency: SkillProficiency | null;
  created_at: string;
  updated_at: string;
}

export interface TailorCvResult {
  tailored_cv: string;
  cover_letter: string | null;
  provider: string;
  saved_cv_id: string | null;
}

export interface JobSearchFilter {
  id: string;
  name: string;
  title_keywords: string | null;
  locations: string | null;
  keywords: string | null;
  remote: boolean;
  salary_min: number | null;
  salary_max: number | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Job {
  id: string;
  source: string;
  external_id: string;
  title: string;
  company: string | null;
  location: string | null;
  description: string | null;
  url: string;
  salary_min: number | null;
  salary_max: number | null;
  remote: boolean;
  posted_at: string | null;
  created_at: string;
  updated_at: string;
}

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
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface Offer {
  id: string;
  application_id: string;
  base_salary: number | null;
  bonus: number | null;
  equity: string | null;
  currency: string | null;
  benefits: string | null;
  decision: OfferDecision;
  received_at: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
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

/** Zod schemas for client-side form validation. */
import { z } from 'zod';

import { OFFER_DECISIONS } from './constants';

export const profileSchema = z.object({
  full_name: z.string().trim().max(120, 'Name is too long.').optional(),
});

export const passwordChangeSchema = z
  .object({
    current_password: z.string().min(1, 'Enter your current password.'),
    new_password: z.string().min(8, 'New password must be at least 8 characters.').max(72),
    confirm_password: z.string(),
  })
  .refine((data) => data.new_password === data.confirm_password, {
    message: 'Passwords do not match.',
    path: ['confirm_password'],
  });

const optionalAmount = z
  .union([z.string(), z.number()])
  .optional()
  .transform((value) => {
    if (value === undefined || value === '') return null;
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : null;
  })
  .refine((value) => value === null || value >= 0, { message: 'Must be zero or positive.' });

export const offerSchema = z.object({
  application_id: z.string().uuid('Select an application.'),
  base_salary: optionalAmount,
  bonus: optionalAmount,
  currency: z
    .string()
    .trim()
    .length(3, 'Use a 3-letter currency code.')
    .optional()
    .or(z.literal('')),
  equity: z.string().trim().max(200).optional(),
  benefits: z.string().trim().max(20_000).optional(),
  decision: z.enum(OFFER_DECISIONS as [string, ...string[]]),
});

export type ProfileFormValues = z.infer<typeof profileSchema>;
export type PasswordFormValues = z.infer<typeof passwordChangeSchema>;
export type OfferFormValues = z.infer<typeof offerSchema>;

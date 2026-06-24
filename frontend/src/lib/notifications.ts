/**
 * Native local-notification scheduling for interview reminders.
 *
 * On iOS and Android (Capacitor) this calls the LocalNotifications plugin via
 * the runtime-injected `window.Capacitor.Plugins` bridge — no static import is
 * needed, so the web bundle stays the same size and the SPA build never
 * depends on @capacitor/local-notifications being installed.
 *
 * On the web (or on a native build without the plugin), `scheduleInterviewReminder`
 * is a quiet no-op.
 */

import { isNative } from './capacitor-auth';

interface LocalNotificationsPlugin {
  requestPermissions(): Promise<{ display: string }>;
  schedule(opts: {
    notifications: Array<{
      id: number;
      title: string;
      body: string;
      schedule?: { at: Date };
    }>;
  }): Promise<unknown>;
  cancel?(opts: { notifications: Array<{ id: number }> }): Promise<unknown>;
}

interface CapacitorRuntime {
  Plugins?: { LocalNotifications?: LocalNotificationsPlugin };
}

interface CapWindow extends Window {
  Capacitor?: CapacitorRuntime;
}

function getPlugin(): LocalNotificationsPlugin | null {
  if (typeof window === 'undefined') return null;
  const plugin = (window as CapWindow).Capacitor?.Plugins?.LocalNotifications;
  return plugin ?? null;
}

/**
 * Hash a UUID string into a 31-bit signed integer so we can use a stable
 * notification ID that LocalNotifications can dedupe across launches.
 */
export function hashId(uuid: string): number {
  let hash = 0;
  for (let i = 0; i < uuid.length; i++) {
    hash = ((hash << 5) - hash + uuid.charCodeAt(i)) | 0;
  }
  return Math.abs(hash) || 1;
}

export interface InterviewReminder {
  id: string;
  title: string;
  scheduledAt: Date | string;
  minutesBefore?: number;
}

/**
 * Schedule one local notification ahead of an interview.
 *
 * Idempotent — re-calling with the same interview id replaces the previous
 * scheduled notification. No network or platform call happens on the web.
 */
export async function scheduleInterviewReminder(reminder: InterviewReminder): Promise<void> {
  if (!isNative()) return;
  const plugin = getPlugin();
  if (!plugin) return;

  const at = new Date(reminder.scheduledAt);
  if (Number.isNaN(at.getTime())) return;
  const minutesBefore = reminder.minutesBefore ?? 60;
  const fireAt = new Date(at.getTime() - minutesBefore * 60_000);
  if (fireAt.getTime() <= Date.now()) return;

  try {
    const perm = await plugin.requestPermissions();
    if (perm.display !== 'granted') return;
    await plugin.schedule({
      notifications: [
        {
          id: hashId(reminder.id),
          title: 'Upcoming interview',
          body: reminder.title,
          schedule: { at: fireAt },
        },
      ],
    });
  } catch {
    // Plugin missing on this device or scheduling rejected — fail closed.
  }
}

/**
 * Schedule reminders for a list of upcoming interviews. Convenient to call
 * from a `useEffect` once interviews load on the Interviews page.
 */
export async function scheduleInterviewReminders(
  reminders: InterviewReminder[]
): Promise<void> {
  if (!isNative()) return;
  await Promise.all(reminders.map((r) => scheduleInterviewReminder(r)));
}

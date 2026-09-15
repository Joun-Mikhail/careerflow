import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { queryKeys } from '@/lib/queryClient';
import { contactsApi, type ContactFilters, type ContactInput } from '@/services/contacts';

export function useContacts(filters: ContactFilters = {}) {
  return useQuery({
    queryKey: queryKeys.contacts(filters),
    queryFn: () => contactsApi.list(filters),
  });
}

/** Every mutation invalidates the whole list, since edits can reorder it. */
function useInvalidateContacts() {
  const qc = useQueryClient();
  return () => qc.invalidateQueries({ queryKey: ['contacts'] });
}

export function useCreateContact() {
  const invalidate = useInvalidateContacts();
  return useMutation({
    mutationFn: (input: ContactInput) => contactsApi.create(input),
    onSuccess: invalidate,
  });
}

export function useUpdateContact() {
  const invalidate = useInvalidateContacts();
  return useMutation({
    mutationFn: ({ id, input }: { id: string; input: Partial<ContactInput> }) =>
      contactsApi.update(id, input),
    onSuccess: invalidate,
  });
}

export function useDeleteContact() {
  const invalidate = useInvalidateContacts();
  return useMutation({
    mutationFn: (id: string) => contactsApi.remove(id),
    onSuccess: invalidate,
  });
}

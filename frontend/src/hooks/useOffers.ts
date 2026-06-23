import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { queryKeys } from '@/lib/queryClient';
import { offersApi } from '@/services/offers';
import type { OfferInput, OfferListParams } from '@/services/offers';

export function useOffers(params: OfferListParams = {}) {
  return useQuery({
    queryKey: queryKeys.offers(params),
    queryFn: () => offersApi.list(params),
  });
}

export function useApplicationOffers(applicationId: string) {
  return useQuery({
    queryKey: queryKeys.offersForApplication(applicationId),
    queryFn: () => offersApi.listForApplication(applicationId),
  });
}

export function useCreateOffer(applicationId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (input: OfferInput) => offersApi.create(applicationId, input),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['offers'] }),
  });
}

export function useUpdateOffer() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, input }: { id: string; input: OfferInput }) =>
      offersApi.update(id, input),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['offers'] }),
  });
}

export function useDeleteOffer() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => offersApi.remove(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['offers'] }),
  });
}

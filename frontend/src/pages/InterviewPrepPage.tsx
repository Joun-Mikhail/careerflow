import { useMemo, useState } from 'react';
import type { FormEvent } from 'react';

import { EmptyState, ErrorState } from '@/components/feedback/States';
import { TableSkeleton } from '@/components/feedback/Skeletons';
import { CheckSquareIcon, PlusIcon, TrashIcon } from '@/components/icons';
import { useToast } from '@/contexts/ToastContext';
import {
  useCreateInterviewQuestion,
  useDeleteInterviewQuestion,
  useInterviewQuestions,
  useUpdateInterviewQuestion,
} from '@/hooks/useInterviewQuestions';
import { parseTags, tagCounts } from '@/lib/tags';
import { ApiError } from '@/services/api';

import type { InterviewQuestion } from '@/lib/types';

function errorMessage(err: unknown, fallback: string): string {
  return err instanceof ApiError ? err.message : fallback;
}

export function InterviewPrepPage() {
  const toast = useToast();
  const [activeTag, setActiveTag] = useState('');
  // The unfiltered list feeds the tag rail, so selecting a tag cannot make the
  // other tags disappear and strand the user with no way back.
  const { data: all, isLoading, isError, refetch } = useInterviewQuestions();
  const { data: filtered } = useInterviewQuestions(activeTag ? { tag: activeTag } : {});

  const createQuestion = useCreateInterviewQuestion();
  const updateQuestion = useUpdateInterviewQuestion();
  const deleteQuestion = useDeleteInterviewQuestion();

  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [tags, setTags] = useState('');
  const [openId, setOpenId] = useState<string | null>(null);
  const [draftAnswer, setDraftAnswer] = useState('');

  const questions = activeTag ? (filtered ?? []) : (all ?? []);

  const allTags = useMemo(() => tagCounts(all ?? []), [all]);

  async function handleCreate(event: FormEvent) {
    event.preventDefault();
    if (!question.trim()) {
      toast.error('Write the question first.');
      return;
    }
    try {
      await createQuestion.mutateAsync({
        question: question.trim(),
        answer: answer.trim() || null,
        tags: tags.trim() || null,
      });
      toast.success('Question added.');
      setQuestion('');
      setAnswer('');
      setTags('');
    } catch (err) {
      toast.error(errorMessage(err, 'Could not add that question.'));
    }
  }

  function startEditing(item: InterviewQuestion) {
    const next = openId === item.id ? null : item.id;
    setOpenId(next);
    setDraftAnswer(next ? (item.answer ?? '') : '');
  }

  function saveAnswer(item: InterviewQuestion) {
    updateQuestion.mutate(
      { id: item.id, input: { answer: draftAnswer.trim() || null } },
      {
        onSuccess: () => {
          toast.success('Answer saved.');
          setOpenId(null);
        },
        onError: (e) => toast.error(errorMessage(e, 'Could not save that answer.')),
      },
    );
  }

  function toggleAsked(item: InterviewQuestion) {
    updateQuestion.mutate(
      { id: item.id, input: { asked: !item.asked } },
      { onError: (e) => toast.error(errorMessage(e, 'Could not update that question.')) },
    );
  }

  const askedCount = (all ?? []).filter((q) => q.asked).length;

  return (
    <>
      <div className="page-header">
        <div>
          <h1 className="page-title">Interview prep</h1>
          <p className="page-subtitle">
            Bank the questions you are asked and the answers you want to give.
          </p>
        </div>
      </div>

      <form className="card" onSubmit={handleCreate}>
        <div className="card-body stack" style={{ gap: 'var(--space-3)' }}>
          <div className="field">
            <label className="label" htmlFor="q-text">Question</label>
            <input
              id="q-text"
              className="input"
              value={question}
              placeholder="e.g. Tell me about a time you disagreed with a colleague."
              onChange={(e) => setQuestion(e.target.value)}
              required
            />
          </div>
          <div className="row" style={{ gap: 'var(--space-3)', flexWrap: 'wrap', alignItems: 'flex-end' }}>
            <div className="field" style={{ flex: '1 1 320px' }}>
              <label className="label" htmlFor="q-answer">Your answer (optional)</label>
              <input
                id="q-answer"
                className="input"
                value={answer}
                placeholder="Bullet points are fine — you can refine it later."
                onChange={(e) => setAnswer(e.target.value)}
              />
            </div>
            <div className="field" style={{ flex: '1 1 200px' }}>
              <label className="label" htmlFor="q-tags">Tags</label>
              <input
                id="q-tags"
                className="input"
                value={tags}
                placeholder="behavioural, system design"
                onChange={(e) => setTags(e.target.value)}
              />
            </div>
            <button className="btn btn-primary" type="submit" disabled={createQuestion.isPending}>
              <PlusIcon /> Add question
            </button>
          </div>
        </div>
      </form>

      {allTags.length > 0 && (
        <div className="card">
          <div className="card-body row" style={{ gap: 6, flexWrap: 'wrap', alignItems: 'center' }}>
            <span className="subtle" style={{ marginRight: 4 }}>Filter</span>
            <button
              className={`chip chip--button${activeTag === '' ? ' chip--active' : ''}`}
              onClick={() => setActiveTag('')}
              type="button"
            >
              All ({(all ?? []).length})
            </button>
            {allTags.map(([tag, count]) => (
              <button
                key={tag}
                type="button"
                className={`chip chip--button${activeTag === tag ? ' chip--active' : ''}`}
                onClick={() => setActiveTag(activeTag === tag ? '' : tag)}
              >
                {tag} ({count})
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="card">
        <div className="card-header row-between">
          <span className="card-title">
            {activeTag ? `Tagged “${activeTag}”` : 'Question bank'}
          </span>
          {(all ?? []).length > 0 && (
            <span className="subtle">{askedCount} actually asked</span>
          )}
        </div>
        {isLoading ? (
          <TableSkeleton columns={3} />
        ) : isError ? (
          <ErrorState error={null} onRetry={refetch} />
        ) : questions.length === 0 ? (
          <EmptyState
            icon={<CheckSquareIcon />}
            title={activeTag ? 'Nothing with that tag' : 'No questions yet'}
            description={
              activeTag
                ? 'Clear the filter to see the rest of your bank.'
                : 'Add the questions you expect — or the ones you were just asked.'
            }
          />
        ) : (
          <div className="card-body stack" style={{ gap: 'var(--space-3)' }}>
            {questions.map((item) => (
              <div key={item.id} className="prep-item">
                <div className="row-between" style={{ gap: 'var(--space-3)', alignItems: 'flex-start' }}>
                  <div style={{ flex: 1 }}>
                    <p className="prep-question">{item.question}</p>
                    <div className="row" style={{ gap: 6, flexWrap: 'wrap', marginTop: 6 }}>
                      {item.asked && <span className="chip chip--ok">asked</span>}
                      {parseTags(item.tags).map((tag) => (
                        <span key={tag} className="chip">{tag}</span>
                      ))}
                      {!item.answer && <span className="chip chip--gap">no answer yet</span>}
                    </div>
                  </div>
                  <div className="row" style={{ gap: 4 }}>
                    <button
                      className="btn btn-ghost btn-sm"
                      onClick={() => toggleAsked(item)}
                      title={item.asked ? 'Mark as not yet asked' : 'Mark as actually asked'}
                    >
                      <CheckSquareIcon width={16} height={16} />
                    </button>
                    <button
                      className="btn btn-secondary btn-sm"
                      onClick={() => startEditing(item)}
                      aria-expanded={openId === item.id}
                    >
                      {openId === item.id ? 'Close' : item.answer ? 'Edit answer' : 'Add answer'}
                    </button>
                    <button
                      className="btn btn-ghost btn-sm"
                      title="Delete"
                      onClick={() =>
                        deleteQuestion.mutate(item.id, {
                          onError: (e) => toast.error(errorMessage(e, 'Delete failed.')),
                        })
                      }
                    >
                      <TrashIcon width={16} height={16} />
                    </button>
                  </div>
                </div>

                {openId === item.id ? (
                  <div className="stack" style={{ gap: 'var(--space-2)', marginTop: 'var(--space-3)' }}>
                    <textarea
                      className="input"
                      rows={5}
                      value={draftAnswer}
                      placeholder="What you want to say, in your own words."
                      onChange={(e) => setDraftAnswer(e.target.value)}
                    />
                    <div className="row" style={{ gap: 6 }}>
                      <button
                        className="btn btn-primary btn-sm"
                        onClick={() => saveAnswer(item)}
                        disabled={updateQuestion.isPending}
                      >
                        Save answer
                      </button>
                      <button className="btn btn-ghost btn-sm" onClick={() => setOpenId(null)}>
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  item.answer && <p className="prep-answer">{item.answer}</p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </>
  );
}

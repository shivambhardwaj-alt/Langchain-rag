import React, { useState } from "react";
import {
  BookOpen,
  Brain,
  HelpCircle,
  ShieldAlert,
  Lightbulb,
  GraduationCap,
  Map,
  AlertTriangle,
  ChevronDown,
  ChevronRight,
  CheckCircle2,
  XCircle,
} from "lucide-react";



const badgeColor = (level = "") => {
  const key = String(level).toLowerCase();
  if (["beginner", "easy", "remember", "weak"].includes(key)) return "bg-green-100 text-green-700";
  if (["intermediate", "medium", "understand", "apply", "moderate"].includes(key)) return "bg-yellow-100 text-yellow-700";
  if (["advanced", "hard", "analyze", "evaluate", "create", "strong"].includes(key)) return "bg-red-100 text-red-700";
  return "bg-gray-100 text-gray-700";
};

const Badge = ({ children }) => (
  <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${badgeColor(children)}`}>
    {children}
  </span>
);

const Card = ({ children, className = "" }) => (
  <div className={`border border-gray-200 rounded-xl p-4 bg-white shadow-sm ${className}`}>
    {children}
  </div>
);


const SummaryView = ({ data }) => {
  const text = typeof data === "string" ? data : data?.summary || "";
  return (
    <Card>
      <div className="flex items-center gap-2 mb-3 text-gray-900 font-semibold">
        <BookOpen size={18} /> Summary
      </div>
      <div className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">{text}</div>
    </Card>
  );
};


const ConceptsView = ({ data }) => (
  <div className="space-y-4">
    {data?.concepts?.map((c, i) => (
      <Card key={i}>
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-center gap-2 font-semibold text-gray-900">
            <Brain size={16} /> {c.name}
          </div>
          <Badge>{c.difficulty}</Badge>
        </div>
        <p className="text-sm text-gray-700 mt-2">{c.definition}</p>
        <p className="text-xs text-gray-500 mt-2 italic">{c.importance}</p>
        {c.related_concepts?.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mt-3">
            {c.related_concepts.map((rc, j) => (
              <span key={j} className="text-xs bg-blue-50 text-blue-700 px-2 py-0.5 rounded-full">
                {rc}
              </span>
            ))}
          </div>
        )}
      </Card>
    ))}

    {data?.prerequisite_concepts?.length > 0 && (
      <Card className="bg-amber-50 border-amber-200">
        <div className="flex items-center gap-2 font-semibold text-amber-800 text-sm mb-2">
          <AlertTriangle size={16} /> Assumed prerequisites
        </div>
        <ul className="list-disc list-inside text-sm text-amber-800 space-y-1">
          {data.prerequisite_concepts.map((p, i) => (
            <li key={i}>{p}</li>
          ))}
        </ul>
      </Card>
    )}
  </div>
);


const QuestionsView = ({ data }) => (
  <div className="space-y-3">
    {data?.questions?.map((q, i) => (
      <Card key={i}>
        <div className="flex gap-2 mb-2">
          <Badge>{q.type}</Badge>
          <Badge>{q.bloom_level}</Badge>
        </div>
        <p className="text-sm font-medium text-gray-900">{q.question}</p>
        <p className="text-sm text-gray-600 mt-2 border-l-2 border-gray-200 pl-3">{q.answer}</p>
      </Card>
    ))}
  </div>
);


const QuizView = ({ data }) => {
  const [selected, setSelected] = useState({});
  const [revealed, setRevealed] = useState({});

  const choose = (qi, opt) => {
    setSelected((s) => ({ ...s, [qi]: opt }));
    setRevealed((r) => ({ ...r, [qi]: true }));
  };

  return (
    <div className="space-y-4">
      {data?.quiz?.map((q, qi) => (
        <Card key={qi}>
          <p className="text-sm font-medium text-gray-900 mb-3">
            {qi + 1}. {q.question}
          </p>
          <div className="space-y-2">
            {q.options?.map((opt, oi) => {
              const isSelected = selected[qi] === opt;
              const isCorrect = opt === q.correct_answer;
              const showState = revealed[qi];
              return (
                <button
                  key={oi}
                  onClick={() => choose(qi, opt)}
                  className={`w-full text-left text-sm px-3 py-2 rounded-lg border flex items-center justify-between
                    ${showState && isCorrect ? "border-green-400 bg-green-50" : ""}
                    ${showState && isSelected && !isCorrect ? "border-red-400 bg-red-50" : ""}
                    ${!showState ? "border-gray-200 hover:border-gray-400" : ""}`}
                >
                  {opt}
                  {showState && isCorrect && <CheckCircle2 size={16} className="text-green-600" />}
                  {showState && isSelected && !isCorrect && <XCircle size={16} className="text-red-600" />}
                </button>
              );
            })}
          </div>
          {revealed[qi] && q.explanation && (
            <p className="text-xs text-gray-500 mt-3 italic">{q.explanation}</p>
          )}
        </Card>
      ))}
    </div>
  );
};


const FlashcardsView = ({ data }) => {
  const [flipped, setFlipped] = useState({});
  const toggle = (i) => setFlipped((f) => ({ ...f, [i]: !f[i] }));

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
      {data?.flashcards?.map((c, i) => (
        <button
          key={i}
          onClick={() => toggle(i)}
          className="text-left border border-gray-200 rounded-xl p-4 bg-white shadow-sm hover:shadow-md transition-shadow"
        >
          <div className="flex items-center justify-between mb-2">
            <Badge>{c.card_type}</Badge>
            <Badge>{c.difficulty}</Badge>
          </div>
          <p className="text-sm text-gray-900 font-medium">{flipped[i] ? c.back : c.front}</p>
          <p className="text-xs text-gray-400 mt-2">
            {flipped[i] ? "tap to see question" : "tap to reveal answer"}
          </p>
        </button>
      ))}
    </div>
  );
};


const CounterArgumentsView = ({ data }) => {
  if (data?.has_clear_argumentative_thesis === false) {
    return (
      <Card className="text-sm text-gray-600">
        This document is descriptive rather than argumentative, so there are no strong counter-arguments to raise.
      </Card>
    );
  }
  return (
    <div className="space-y-4">
      <Card className="bg-gray-50">
        <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">Document thesis</div>
        <p className="text-sm text-gray-800">{data?.document_thesis}</p>
      </Card>
      {data?.counter_arguments?.map((c, i) => (
        <Card key={i}>
          <div className="flex items-center justify-between gap-2 mb-2">
            <div className="flex items-center gap-2 text-sm font-semibold text-gray-900">
              <ShieldAlert size={16} /> Claim challenged
            </div>
            <Badge>{c.strength}</Badge>
          </div>
          <p className="text-sm text-gray-700 italic mb-2">{c.original_claim}</p>
          <p className="text-sm text-gray-800">{c.counter_argument}</p>
          <p className="text-xs text-gray-500 mt-2">{c.supporting_reasoning}</p>
        </Card>
      ))}
    </div>
  );
};


const ExplainView = ({ data, icon: Icon, label }) => {
  const text = typeof data === "string" ? data : data?.explanation || data?.text || "";
  return (
    <Card>
      <div className="flex items-center gap-2 mb-3 text-gray-900 font-semibold">
        <Icon size={18} /> {label}
      </div>
      <div className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">{text}</div>
    </Card>
  );
};


const MissingKnowledgeView = ({ data }) => (
  <div className="space-y-3">
    {data?.gaps?.map((g, i) => (
      <Card key={i}>
        <div className="flex items-center gap-2 font-semibold text-gray-900 text-sm mb-2">
          <HelpCircle size={16} /> {g.gap}
        </div>
        <p className="text-sm text-gray-700">{g.why_it_matters}</p>
        <p className="text-xs text-blue-600 mt-2">Look up: {g.suggested_lookup}</p>
      </Card>
    ))}
    {data?.user_likely_already_knows?.length > 0 && (
      <Card className="bg-green-50 border-green-200">
        <div className="text-xs font-semibold text-green-800 uppercase tracking-wide mb-2">Already covered</div>
        <div className="flex flex-wrap gap-1.5">
          {data.user_likely_already_knows.map((k, i) => (
            <span key={i} className="text-xs bg-white text-green-700 border border-green-200 px-2 py-0.5 rounded-full">
              {k}
            </span>
          ))}
        </div>
      </Card>
    )}
  </div>
);

const MindMapNode = ({ node, allNodes, depth }) => {
  const [open, setOpen] = useState(true);
  const children = allNodes.filter((n) => n.parent_id === node.id);

  return (
    <div className={depth > 0 ? "ml-5 border-l border-gray-200 pl-4 mt-2" : "mt-2"}>
      <div className="flex items-center gap-1.5">
        {children.length > 0 ? (
          <button onClick={() => setOpen(!open)} className="text-gray-400">
            {open ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
          </button>
        ) : (
          <span className="w-3.5 h-1.5 border-b border-gray-300 inline-block" />
        )}
        <span className={`text-sm ${depth === 0 ? "font-bold text-gray-900" : "text-gray-700"}`}>{node.label}</span>
      </div>
      {open && children.map((c) => <MindMapNode key={c.id} node={c} allNodes={allNodes} depth={depth + 1} />)}
    </div>
  );
};

const MindMapView = ({ data }) => {
  const root = data?.nodes?.find((n) => !n.parent_id);
  if (!root) return <Card className="text-sm text-gray-500">No mind map data.</Card>;
  return (
    <Card>
      <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">{data.title}</div>
      <MindMapNode node={root} allNodes={data.nodes} depth={0} />
    </Card>
  );
};


const RoadmapView = ({ data }) => {
  if (!data) return null;

  return (
    <div className="space-y-5">
      {/* Goal */}
      <Card className="border-blue-200 bg-blue-50">
        <div className="flex items-center gap-2 text-lg font-semibold text-blue-900">
          <Map size={18} />
          Learning Goal
        </div>

        <p className="text-sm text-gray-700 mt-2">
          {data.goal}
        </p>
      </Card>

      {/* Progress */}
      <Card className="border-green-200 bg-green-50">
        <div className="font-semibold text-green-800">
          Current Progress
        </div>

        <p className="text-sm text-green-700 mt-1">
          You are currently on <strong>Step {data.current_position_step}</strong>
        </p>
      </Card>

    
      <div className="space-y-0">
        {data.steps?.map((step, index) => {
          const completed =
            step.step_number < data.current_position_step;

          const current =
            step.step_number === data.current_position_step;

          return (
            <div
              key={step.step_number}
              className="flex gap-4"
            >
           
              <div className="flex flex-col items-center">
                <div
                  className={`w-9 h-9 rounded-full flex items-center justify-center text-white font-semibold
                  ${
                    completed
                      ? "bg-green-600"
                      : current
                      ? "bg-blue-600"
                      : "bg-gray-400"
                  }`}
                >
                  {step.step_number}
                </div>

                {index !== data.steps.length - 1 && (
                  <div className="flex-1 w-px bg-gray-300" />
                )}
              </div>

        
              <Card
                className={`flex-1 mb-5 ${
                  current
                    ? "border-blue-400 shadow-md"
                    : ""
                }`}
              >
                <div className="flex justify-between items-center">
                  <h3 className="font-semibold text-gray-900">
                    {step.title}
                  </h3>

                  <Badge>{step.estimated_time}</Badge>
                </div>

                <p className="text-sm text-gray-700 mt-3">
                  {step.description}
                </p>

                {step.depends_on_steps.length > 0 && (
                  <div className="mt-4">
                    <div className="text-xs font-semibold text-gray-500 uppercase">
                      Prerequisites
                    </div>

                    <div className="flex flex-wrap gap-2 mt-2">
                      {step.depends_on_steps.map((dep) => (
                        <span
                          key={dep}
                          className="bg-gray-100 text-gray-700 px-2 py-1 rounded-full text-xs"
                        >
                          Step {dep}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {step.resources_to_revisit.length > 0 && (
                  <div className="mt-4">
                    <div className="text-xs font-semibold text-gray-500 uppercase">
                      Previous Documents
                    </div>

                    <div className="flex flex-wrap gap-2 mt-2">
                      {step.resources_to_revisit.map((doc, i) => (
                        <span
                          key={i}
                          className="bg-blue-100 text-blue-700 px-2 py-1 rounded-full text-xs"
                        >
                          📄 {doc}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </Card>
            </div>
          );
        })}
      </div>
    </div>
  );
};


const FallbackView = ({ data }) => {
  const text = typeof data === "string" ? data : data?.answer || data?.response || "";
  return (
    <Card>
      <div className="flex items-center gap-2 mb-3 text-gray-900 font-semibold">
        <Lightbulb size={18} /> Answer
      </div>
      <div className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">{text}</div>
    </Card>
  );
};



const MODE_LABELS = {
  summary: "summary",
  concepts: "concepts",
  questions: "questions",
  mindmap: "mindmap",
  quiz: "quiz",
  flashcards: "flashcards",
  counter_arguments: "counterargs",
  explain_simply: "explain_simple",
  explain_technically: "explain_technical",
  missing_knowledge: "missing_knowledge",
  roadmap: "roadmap",
  fallback: "Answer",
};


const ResponseRenderer = ({ mode, data, loading, error }) => {
  if (loading) {
    return (
      <div className="text-sm text-gray-500 flex items-center gap-2 p-4">
        <GraduationCap size={16} className="animate-pulse" /> Generating {MODE_LABELS[mode] || "response"}...
      </div>
    );
  }

  if (error) {
    return <div className="text-sm text-red-600 p-4">{error}</div>;
  }

  if (!data) return null;

  switch (mode) {
    case "summary":
      return <SummaryView data={data} />;
    case "concepts":
      return <ConceptsView data={data} />;
    case "questions":
      return <QuestionsView data={data} />;
    case "mindmap":
      return <MindMapView data={data} />;
    case "quiz":
      return <QuizView data={data} />;
    case "flashcards":
      return <FlashcardsView data={data} />;
    case "counter_arguments":
      return <CounterArgumentsView data={data} />;
    case "explain_simply":
      return <ExplainView data={data} icon={Lightbulb} label="Explained Simply" />;
    case "explain_technically":
      return <ExplainView data={data} icon={GraduationCap} label="Technical Explanation" />;
    case "missing_knowledge":
      return <MissingKnowledgeView data={data} />;
    case "roadmap":
      return <RoadmapView data={data} />;
    default:
      return <FallbackView data={data} />;
  }
};

export default ResponseRenderer;
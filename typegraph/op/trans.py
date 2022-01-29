from ..expr import *
from ..spec import Attr, ConstraintSpec, Op

_concat = ConstraintSpec(
    attrs=[
        Attr('axis', Var(ty=INT, ran=Range(0, IN[0].rank)))
    ],
    in_num=Var(),
    in_ranks=List(IN.num, lambda _: Var()),
    in_dtypes=List(IN.num, lambda _: Var()),
    in_shapes=List(IN.num, lambda _: List(
        IN[0].rank, lambda j: Cond(j == a('axis'), Var(tmpl=True), Var())
    )),
    extra=[],
    out_num=1,
    out_ranks=[IN[0].rank],
    out_dtypes=[IN[0].dtype],
    out_shapes=[
        List(IN[0].rank, lambda j: Cond(
            j == a('axis'),
            ReduceIndex(Range(end=IN.num), ArithOp.ADD, 0, body_f=lambda i: IN[i].shape[j]),
            IN[0].shape[j]
        ))
    ]
)

Op('concatenate', _concat)


def _create_split():
    ind = a('indices_or_sections')
    return ConstraintSpec(
        attrs=[
            Attr('axis', Var(ty=INT, ran=Range(0, IN[0].rank))),
            Attr('indices_or_sections',
                 List(Var(ran=Range(begin=1, end=IN[0].shape[a('axis')])),
                      lambda _: Var(INT, tmpl=True)))
        ],
        in_num=1,
        in_ranks=[Var(ran=Range(begin=1))],
        in_dtypes=[Var()],
        in_shapes=[List(IN[0].rank, lambda _: Var(tmpl=True))],
        extra=[
            ind[0] > 0,
            ForAll(Range(1, Len(ind)), lambda i: ind[i - 1] < ind[i]),
            ind[-1] < IN[0].shape[a('axis')]
        ],
        out_num=Len(ind) + 1,
        out_ranks=List(OUT.num, lambda _: IN[0].rank),
        out_dtypes=List(OUT.num, lambda _: IN[0].dtype),
        out_shapes=List(OUT.num, lambda i: List(IN[0].rank, lambda j: Cond(
            j == a('axis'),
            Cond(i == 0, ind[0],
                 Cond(i == Len(ind), IN[0].shape[j] - ind[-1],
                      ind[i] - ind[i - 1])),
            IN[0].shape[j]
        )))
    )


Op('split', _create_split())

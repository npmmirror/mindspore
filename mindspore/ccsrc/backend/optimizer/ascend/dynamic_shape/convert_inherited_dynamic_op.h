/**
 * Copyright 2022 Huawei Technologies Co., Ltd
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#ifndef MINDSPORE_CCSRC_BACKEND_OPTIMIZER_ASCEND_DYNAMIC_SHAPE_CONVERT_INHERITED_DYNAMIC_OP_H
#define MINDSPORE_CCSRC_BACKEND_OPTIMIZER_ASCEND_DYNAMIC_SHAPE_CONVERT_INHERITED_DYNAMIC_OP_H

#include "ir/anf.h"
#include "backend/optimizer/common/optimizer.h"

namespace mindspore::opt::dynamic_shape {
class ConvertInheritedDynamicOp : public PatternProcessPass {
 public:
  explicit ConvertInheritedDynamicOp(bool multigraph = true)
      : PatternProcessPass("convert_inherited_dynamic_op", multigraph) {}
  ~ConvertInheritedDynamicOp() override = default;
  const BaseRef DefinePattern() const override;
  const AnfNodePtr Process(const FuncGraphPtr &graph, const AnfNodePtr &node, const EquivPtr &) const override;
};
}  // namespace mindspore::opt::dynamic_shape
#endif  // MINDSPORE_CCSRC_BACKEND_OPTIMIZER_ASCEND_DYNAMIC_SHAPE_CONVERT_GENERAL_OP_H

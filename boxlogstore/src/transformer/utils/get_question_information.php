<?php

// This file is part of Moodle - http://moodle.org/
//
// Moodle is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// Moodle is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with Moodle.  If not, see <http://www.gnu.org/licenses/>.

namespace src\transformer\utils;

defined('MOODLE_INTERNAL') || die();

function get_question_information($repo, $slot)
{

    $question = $repo->read_record_by_id('question', $slot->questionid);
// This is for future use. That's why it needs $repo
    // switch ($question->qtype) {
    //     case 'essay':
    //         $qid = $repo->read_record_by_id('qtype_essay_options', $question->id);
    //     case 'gapselect':
    //         $qid = $repo->read_record_by_id('question_gapselect', $question->id);
    //     case 'truefalse':
    //         $qid = $repo->read_record_by_id('question_truefalse', $question->id);
    //     case 'randomsamatch':
    //         $qid = $repo->read_record_by_id('qtype_randomsamatch_options', $question->id);
    //     case 'shortanswer':
    //         $qid = $repo->read_record_by_id('qtype_shortanswer_options', $question->id);
    //     case 'match':
    //         $qid = $repo->read_record_by_id('qtype_match_options', $question->id);
    //     case 'multichoice':
    //     case 'multichoiceset':
    //         $qid = $repo->read_record_by_id('qtype_multiplechoice_options', $question->id);
    //     case 'numerical':
    //         $qid = $repo->read_record_by_id('question_numerical', $question->id);
    //     default:
    //         die();
    // }

    return array(
        "question_id" => $question->id,
        "question_name" => $question->name,
        "question_text" => $question->questiontext
    );
}
